import api from "./api";

export function registerUser({ email, username, password, firstName, lastName, phone }) {

  return api.post("/auth/register", {
    email,
    username,
    password,
    first_name: firstName,
    last_name: lastName,
    phone: phone || null, // optional field — send null when empty
  });
}

export function loginUser(email, password) {
  return api.post("/auth/login", { email, password });
}

/** Log out. Backend revokes the refresh token and clears both cookies. */
export function logoutUser() {
  return api.post("/auth/logout");
}
