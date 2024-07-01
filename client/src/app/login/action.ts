"use server";

import getRealm from "@/utils/realm";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import * as Realm from "realm-web";

export async function loginFormAction(
    prevState: { user?: any; error?: any } | never,
    formData: FormData,
) {
    const cookie = cookies();
    const app = getRealm();
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
        const credentials = Realm.Credentials.emailPassword(email, password);
        const user = await app.logIn(credentials);

        if (user.isLoggedIn) {
            cookie.set("accessToken", user.accessToken!);
            cookie.set("refreshToken", user.refreshToken!);
            return redirect("/") as any;
        }
    } catch (error) {
        if (error instanceof Realm.MongoDBRealmError) {
            return { ...prevState, user: null, error: error.message };
        }
        return { ...prevState, user: null, error: (error as Error).message };
    }
}
