/// <reference path="../pb_data/types.d.ts" />
migrate(
  (db) => {
    const dao = new Dao(db);
    const collection = new Collection({
      name: "airbnb_listing",
      type: "base",
      schema: [
        {
          name: "listing_id",
          type: "text",
          required: true,
        },
        {
          name: "baths",
          type: "number",
        },
        {
          name: "beds",
          type: "number",
        },
        {
          name: "latitude",
          type: "text",
        },
        {
          name: "location",
          type: "text",
        },
        {
          name: "longitude",
          type: "text",
        },
        {
          name: "name",
          type: "text",
        },
        {
          name: "person_capacity",
          type: "number",
        },
        {
          name: "registration_number",
          type: "text",
        },
        {
          name: "room_type",
          type: "text",
        },
        {
          name: "title",
          type: "text",
        },
      ],
    });
    dao.saveCollection(collection);
  },
  (db) => {
    console.log("Rollback");
  }
);
