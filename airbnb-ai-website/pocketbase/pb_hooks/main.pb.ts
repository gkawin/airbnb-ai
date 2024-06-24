/// <reference path="../pb_data/types.d.ts" />

routerAdd("GET", "/api/pocketbase", async (c) => {
  let name = c.pathParam("name");
  return c.json(200, { message: "Hello " + name });
});
