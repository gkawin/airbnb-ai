import { cookies } from "next/headers";
import * as Realm from "realm-web";

export default function getRealm() {
    const cookie = cookies();
    const app = Realm.getApp(process.env.NEXT_PUBLIC_REALM_APP_ID || "");
    if (app.currentUser) {
        cookie.set("accessToken", app.currentUser.accessToken!);
    }
    return app;
}
