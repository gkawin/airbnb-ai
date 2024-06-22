import { cookies } from "next/headers";
import Pocketbase from "pocketbase";

export default async function getPocketbase() {
  const pb = new Pocketbase(process.env.NEXT_PUBLIC_POCKET_BASE_URL);
  const isServer = typeof window === "undefined";

  if (isServer) {
    const cookieStore = cookies();
    const cookieName = "pb_auth";
    pb.authStore.loadFromCookie(cookieName);

    // send back the default 'pb_auth' cookie to the client with the latest store state
    pb.authStore.onChange(() => {
      cookieStore.set(
        cookieName,
        pb.authStore.exportToCookie({
          secure: true,
          httpOnly: true,
          sameSite: "strict",
        })
      );
    });
  }

  try {
    // get an up-to-date auth store state by verifying and refreshing the loaded auth model (if any)
    pb.authStore.isValid && (await pb.collection("users").authRefresh());
  } catch (_) {
    // clear the auth store on failed refresh
    pb.authStore.clear();
  }

  return pb;
}
