import json
import pandas as pd
import os
import argparse
import logging
from utils import setup_logging, read_jsonl
from typing import List
import time

LOG_FILE_PATH = "../../logs/parsing_listing_info.log"


def parse_arguments():
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description='Parse Airbnb listing house rules.')
    parser.add_argument('--output_path', type=str, default='../../data/parse_listings',
                        help='Path to save the parsed jsonl files with listing descriptions, amenities and house rules')
    parser.add_argument('--data_path', type=str, default='../../data/listing_page_jsons',
                        help='Path to the the folder containing downloaded listings jsonls')
    return parser.parse_args()


def safe_get(dictionary: dict, keys: List[str], default=None) -> dict:
    """
    Safely get a value from a nested dictionary using a list of keys.

    Args:
        dictionary (dict): The dictionary to search.
        keys (List[str]): A list of keys representing the path to the desired value.
        default: The default value to return if any key is not found. Defaults to None.

    Returns:
        dict: The value found at the specified path or the default value.
    """
    for key in keys:
        if dictionary is not None and key in dictionary:
            dictionary = dictionary[key]
        else:
            return default
    return dictionary


def replace_line_breaks(initial_dict: dict) -> dict:
    """
    Replace line breaks in the values of a dictionary with a specified replacement symbol.

    Args:
        initial_dict (dict): The dictionary whose values need line breaks replaced.

    Returns:
        dict: The dictionary with line breaks replaced in its values.
    """
    LINE_BREAK_REPLACEMENT_SYMBOL = ' %%% '

    for key in initial_dict.keys():
        if type(initial_dict[key]) == list:
            initial_dict[key] = [part.replace('\n', LINE_BREAK_REPLACEMENT_SYMBOL) 
                                 for part in initial_dict[key]]
        else:
            initial_dict[key] = initial_dict[key].replace('\n', LINE_BREAK_REPLACEMENT_SYMBOL)

    return initial_dict


def parse_house_rules(listing_id: str, presentation: dict) -> dict:
    """
    Parse house rules from the presentation dictionary.

    Args:
        listing_id (str): The ID of the listing.
        presentation (dict): The presentation data from which to extract house rules.

    Returns:
        dict: A dictionary of parsed house rules.
    """
    house_rules_dict = {}
    sections = safe_get(presentation, ['stayProductDetailPage', 'sections', 'sections'], [])

    house_rules_section = None
    for section in sections:
        if safe_get(section, ['section', '__typename']) == 'PoliciesSection':
            house_rules_section = safe_get(section, ['section'])
            if house_rules_section:
                logging.info(f"{listing_id=} house rules section found")
                break

    if not house_rules_section:
        logging.error(f"No PoliciesSection found for {listing_id=}.")
        return house_rules_dict

    house_rules_sections = safe_get(house_rules_section, ['houseRulesSections'], [])
    for house_rules_item in house_rules_sections:
        title = safe_get(house_rules_item, ['title'])
        if title:
            house_rule_name = f"{title.lower().replace(' ', '_')}_house_rule"
            items = safe_get(house_rules_item, ['items'], [])

            items_list = []
            for item in items:
                item_title = safe_get(item, ['title'])
                subtitle = safe_get(item, ['subtitle'])
                if subtitle:
                    items_list.append(': '.join([item_title, subtitle]))
                else:
                    items_list.append(item_title)

                # Handle additional rules within the same loop
                if item_title == 'Additional rules':
                    additional_rules_text = safe_get(item, ['html', 'htmlText'])
                    if additional_rules_text:
                        items_list.append(additional_rules_text)

            house_rules_dict[house_rule_name] = items_list

    house_rules_dict = replace_line_breaks(house_rules_dict)

    return house_rules_dict


def parse_amenities(listing_id: str, presentation: dict) -> dict:
    """
    Parse amenities from the presentation dictionary.

    Args:
        listing_id (str): The ID of the listing.
        presentation (dict): The presentation data from which to extract amenities.

    Returns:
        dict: A dictionary of parsed amenities.
    """
    amenities_dict = {}
    sections = safe_get(presentation, ['stayProductDetailPage', 'sections', 'sections'], [])

    amenities_section = None
    for section in sections:
        if safe_get(section, ['section', '__typename']) == 'AmenitiesSection':
            amenities_section = safe_get(section, ['section'])
            if amenities_section:
                logging.info(f"{listing_id=} AmenitiesSection found")
                break

    if not amenities_section or 'seeAllAmenitiesGroups' not in amenities_section:
        logging.error(f"AmenitiesSection not found or missing 'seeAllAmenitiesGroups' key in {listing_id=}. {presentation=}")
        return amenities_dict

    amenities_groups = safe_get(amenities_section, ['seeAllAmenitiesGroups'], [])
    for amenity_item in amenities_groups:
        title = safe_get(amenity_item, ['title'])
        if title:
            amenity_name = f"{title.lower().replace(' ', '_')}_amenities"
            amenities_list = [item['title'] for item in safe_get(amenity_item, ['amenities'], [])]
            amenities_dict[amenity_name] = amenities_list

    amenities_dict = replace_line_breaks(amenities_dict)
    
    return amenities_dict


def parse_description(listing_id: str, presentation: dict) -> dict:
    """
    Parse description from the presentation dictionary.

    Args:
        listing_id (str): The ID of the listing.
        presentation (dict): The presentation data from which to extract descriptions.

    Returns:
        dict: A dictionary of parsed descriptions.
    """
    description_dict = {}

    # Extract selected description sections
    sections = safe_get(presentation, ['stayProductDetailPage', 'sections', 'sections'], [])
    selected_description_sections = [
        section for section in sections
        if safe_get(section, ['sectionId']) == 'DESCRIPTION_MODAL'
    ]

    if not selected_description_sections:
        logging.error(f"No DESCRIPTION_MODAL sections found in presentation {listing_id=}. {presentation=}")
        return description_dict

    logging.info(f"{listing_id} Number of selected description sections: {len(selected_description_sections)}")
    selected_description_section = selected_description_sections[0]

    # Extract items from the selected description section
    items = safe_get(selected_description_section, ['section', 'items'], [])
    logging.info(f"{listing_id} Number of items in selected description section: {len(items)}")

    for n, item in enumerate(items):
        html_text = safe_get(item, ['html', 'htmlText'])
        if html_text:
            title = safe_get(item, ['title'])
            key = f"{title.lower().replace(' ', '_')}_description" if title else "place_description"
            description_dict[key] = html_text

    description_dict = replace_line_breaks(description_dict)
    
    return description_dict


def get_listing_presentation(listing_info_json: object, listing_id: str) -> object:
    """
    Extract the presentation data from the listing information JSON.

    Args:
        listing_info_json (object): The JSON object containing listing information.
        listing_id (str): The ID of the listing.

    Returns:
        object: The presentation data or None if extraction fails.
    """
    try:
        # Extract the presentation data
        presentation = listing_info_json[0]['root > core-guest-spa'][1][1]['niobeMinimalClientData'][1][1]['data'][
            'presentation']
    except Exception as ex:
        logging.error(f"{listing_id=} can't get presentation. Error: {ex.with_traceback()}")
        return

    return presentation


def parse_listing(listing_info_json: object, listing_id: str) -> dict:
    """
    Parse listing information from the provided JSON object and listing ID.

    This function extracts and consolidates various pieces of information about an Airbnb listing
    such as house rules, description, and amenities. It utilizes helper functions to parse specific
    sections of the listing's presentation data.

    Args:
        listing_info_json (object): The JSON object containing listing information.
        listing_id (str): The ID of the listing.

    Returns:
        dict: A dictionary containing parsed information about the listing, including house rules,
              description, and amenities.
    """
    presentation = get_listing_presentation(listing_info_json, listing_id)

    parcing_dict = {'listing_id': listing_id}

    # house_rules_dict
    house_rules_dict = parse_house_rules(listing_id, presentation)
    logging.info(f"{listing_id=} house_rules_dict processed {house_rules_dict=}")
    if house_rules_dict:
        parcing_dict.update(house_rules_dict)

    # description_dict
    description_dict = parse_amenities(listing_id, presentation)
    logging.info(f"{listing_id=} description_dict processed {description_dict=}")
    if description_dict:
        parcing_dict.update(description_dict)

    # amenities_dict
    amenities_dict = parse_description(listing_id, presentation)
    logging.info(f"{listing_id=} amenities_dict processed {amenities_dict=}")
    if amenities_dict:
        parcing_dict.update(amenities_dict)

    return parcing_dict


def main():
    """
    Main function to parse Airbnb listing descriptions, amenities, and house rules, and save them to files.
    """
    # Parse command-line arguments
    args = parse_arguments()
    setup_logging(LOG_FILE_PATH)

    logging.info(f"{args=}")

    # Create the output directory if it doesn't exist
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    # Create a file name with the current date and time
    current_time = time.localtime()
    time_str = time.strftime("%Y%m%d_%H%M%S", current_time)
    output_file_path = os.path.join(args.output_path, f'description_amenities_house_rules_{time_str}.jsonl')

    # Create listing_id list
    listing_id_json_list = [jsonl_filepath
                            for jsonl_filepath in os.listdir(args.data_path) if jsonl_filepath.endswith('.jsonl')]
    logging.info(f"{len(listing_id_json_list)=}")

    total_listings = len(listing_id_json_list)

    # Loop through each listing ID and process it
    try:
        for count, listing_id_json_file in enumerate(listing_id_json_list, start=1):

            listing_id = listing_id_json_file.replace('.jsonl', '')
            logging.info(f"Starting {listing_id_json_file=}, {listing_id=} ({count}/{total_listings})")

            # Open .jsonl file
            json_file_path = os.path.join(args.data_path, listing_id_json_file)
            listing_info_json = read_jsonl(json_file_path)

            # Main parsing logic
            parcing_dict = parse_listing(listing_info_json, listing_id)
            
            # Write the extracted data to the output file
            with open(output_file_path, 'a') as file:  # Open file in append mode
                file.write(json.dumps(parcing_dict) + '\n')

            logging.info(f"{listing_id=} added")

    except Exception as ex:
        logging.error(f"For loop failed. Error: {ex.with_traceback()}")
        return


if __name__ == '__main__':
    main()