import firebase from "firebase-admin";
import { storage } from "firebase-functions/v2";

firebase.initializeApp();

export const load_data_to_firestore = storage.onObjectFinalized(
  {
    region: "us-west1",
    bucket: "codebc-airbnb-ai.appspot.com",
    ingressSettings: "ALLOW_INTERNAL_ONLY",
  },
  async (object) => {
    const file = object;
    const filePath = file.name;
    const fileName = filePath.split("/").pop();
    const tempFilePath = `/tmp/${fileName}`;

    const firestore = firebase.firestore();
    const collection = firestore.collection("data");
    const data = require(tempFilePath);

    await collection.doc(fileName).set(data);
  }
);
