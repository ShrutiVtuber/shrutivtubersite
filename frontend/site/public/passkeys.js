/* Passkeys in the browser.
 *
 * The only JavaScript on the sign-in surfaces, and it is unavoidable:
 * `navigator.credentials` has no HTML form equivalent. Everything it enhances
 * still works with it switched off — the password and emailed-link paths are
 * plain forms, and the passkey controls hide themselves when the browser
 * cannot do WebAuthn rather than offering a button that fails.
 *
 * Deliberately dependency-free and un-bundled: it is loaded with `is:inline`
 * on three pages, and a library for six functions of base64 would be the
 * larger cost.
 */
(function () {
  "use strict";

  var supported =
    typeof window.PublicKeyCredential === "function" &&
    typeof navigator.credentials?.create === "function";

  /* WebAuthn speaks ArrayBuffer; JSON speaks base64url. These four are the
     whole translation layer. */
  function toBuffer(value) {
    var padded = value.replace(/-/g, "+").replace(/_/g, "/");
    while (padded.length % 4) padded += "=";
    var binary = atob(padded);
    var bytes = new Uint8Array(binary.length);
    for (var i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return bytes.buffer;
  }

  function fromBuffer(buffer) {
    var bytes = new Uint8Array(buffer);
    var binary = "";
    for (var i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
    return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }

  function decodeCreation(options) {
    options.challenge = toBuffer(options.challenge);
    options.user.id = toBuffer(options.user.id);
    (options.excludeCredentials || []).forEach(function (c) { c.id = toBuffer(c.id); });
    return options;
  }

  function decodeRequest(options) {
    options.challenge = toBuffer(options.challenge);
    (options.allowCredentials || []).forEach(function (c) { c.id = toBuffer(c.id); });
    return options;
  }

  function encodeRegistration(credential) {
    return {
      id: credential.id,
      rawId: fromBuffer(credential.rawId),
      type: credential.type,
      response: {
        clientDataJSON: fromBuffer(credential.response.clientDataJSON),
        attestationObject: fromBuffer(credential.response.attestationObject),
        transports: credential.response.getTransports
          ? credential.response.getTransports()
          : [],
      },
      clientExtensionResults: credential.getClientExtensionResults(),
    };
  }

  function encodeAssertion(credential) {
    return {
      id: credential.id,
      rawId: fromBuffer(credential.rawId),
      type: credential.type,
      response: {
        clientDataJSON: fromBuffer(credential.response.clientDataJSON),
        authenticatorData: fromBuffer(credential.response.authenticatorData),
        signature: fromBuffer(credential.response.signature),
        userHandle: credential.response.userHandle
          ? fromBuffer(credential.response.userHandle)
          : null,
      },
      clientExtensionResults: credential.getClientExtensionResults(),
    };
  }

  async function postJson(url, body) {
    var response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: body === undefined ? "{}" : JSON.stringify(body),
    });
    var parsed = await response.json().catch(function () { return null; });
    if (!response.ok) {
      var error = new Error((parsed && parsed.detail) || "That did not work.");
      error.handled = true;
      throw error;
    }
    return parsed;
  }

  /* A cancelled prompt is not an error to report. Someone who dismisses Face ID
     has changed their mind, and telling them something went wrong is both
     untrue and alarming. */
  function isCancellation(error) {
    return (
      error &&
      (error.name === "NotAllowedError" || error.name === "AbortError")
    );
  }

  function say(element, message, kind) {
    if (!element) return;
    element.textContent = message || "";
    element.hidden = !message;
    element.className = kind === "bad" ? "pk-msg pk-bad" : "pk-msg";
  }

  async function register(prefix, label, status) {
    var options = decodeCreation(await postJson(prefix + "/register/options"));
    var credential = await navigator.credentials.create({ publicKey: options });
    await postJson(prefix + "/register", {
      credential: encodeRegistration(credential),
      label: label || "",
    });
    say(status, "Passkey added.");
    setTimeout(function () { window.location.reload(); }, 600);
  }

  async function signIn(prefix, destination, status) {
    var options = decodeRequest(await postJson(prefix + "/signin/options"));
    var credential = await navigator.credentials.get({ publicKey: options });
    await postJson(prefix + "/signin", { credential: encodeAssertion(credential) });
    window.location.assign(destination);
  }

  function wire() {
    /* The three surfaces that use this each include the script, and two of
       them can appear on one page. Wiring twice would fire every handler
       twice — one prompt, two sign-in attempts, the second failing on a
       spent challenge. */
    if (window.__shrutiPasskeysWired) return;
    window.__shrutiPasskeysWired = true;

    /* No WebAuthn: reveal nothing. The elements start hidden, so a browser
       without it simply never sees a passkey control — which is better than a
       greyed-out one that needs explaining. */
    if (!supported) return;

    document.querySelectorAll("[data-passkey-block]").forEach(function (el) {
      el.hidden = false;
    });

    document.querySelectorAll("[data-passkey-signin]").forEach(function (button) {
      button.addEventListener("click", async function (event) {
        event.preventDefault();
        var status = document.querySelector(button.dataset.passkeyStatus || "#pk-status");
        var prefix = button.dataset.passkeyPrefix || "/api/passkeys";
        button.disabled = true;
        say(status, "");
        try {
          await signIn(prefix, button.dataset.passkeyNext || "/account", status);
        } catch (error) {
          if (!isCancellation(error)) {
            say(
              status,
              error.handled
                ? error.message
                : "That passkey could not be used on this device.",
              "bad"
            );
          }
          button.disabled = false;
        }
      });
    });

    document.querySelectorAll("[data-passkey-add]").forEach(function (button) {
      button.addEventListener("click", async function (event) {
        event.preventDefault();
        var status = document.querySelector(button.dataset.passkeyStatus || "#pk-status");
        var prefix = button.dataset.passkeyPrefix || "/api/passkeys";
        var field = document.querySelector(button.dataset.passkeyLabel || "#pk-label");
        button.disabled = true;
        say(status, "");
        try {
          await register(prefix, field ? field.value : "", status);
        } catch (error) {
          if (!isCancellation(error)) {
            say(
              status,
              error.handled ? error.message : "That passkey could not be registered.",
              "bad"
            );
          }
          button.disabled = false;
        }
      });
    });

    document.querySelectorAll("[data-passkey-remove]").forEach(function (button) {
      button.addEventListener("click", async function (event) {
        event.preventDefault();
        var status = document.querySelector("#pk-status");
        var prefix = button.dataset.passkeyPrefix || "/api/passkeys";
        var response = await fetch(prefix + "/" + button.dataset.passkeyRemove, {
          method: "DELETE",
          credentials: "same-origin",
        });
        if (response.ok) return window.location.reload();
        var parsed = await response.json().catch(function () { return null; });
        say(status, (parsed && parsed.detail) || "That did not remove.", "bad");
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire);
  } else {
    wire();
  }
})();
