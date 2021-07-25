// ==UserScript==
// @name         Twitch Popout Chroma
// @description  Adds a black outline to white text, and makes the background blue (had the best results chroma keying blue in OBS than any other color.)
// @include      https://www.twitch.tv/popout/*
// @namespace    Edness
// @version      1.0 (2021-07-19)
// @grant        GM_addStyle
// ==/UserScript==

// This script exists because I am too lazy to use anything else that would have
// far better results.  Also mostly pieced together from various other scripts.

if (typeof GM_addStyle == "undefined") {
  this.GM_addStyle = (aCss) => {
    "use strict";
    let head = document.getElementsByTagName("head")[0];
    if (head) {
      let style = document.createElement("style");
      style.textContent = aCss;
      head.appendChild(style);
      return style;
    }
    return null;
  };
}

GM_addStyle ( `
  .chat-line__message, .sc-AxirZ {
    text-shadow:  1px  3px 0px #000,  2px  2px 0px #000,  3px  1px 0px #000,  3px  0px 0px #000,  3px -1px 0px #000,  2px -2px 0px #000,  1px -3px 0px #000,
                 -1px  3px 0px #000, -2px  2px 0px #000, -3px  1px 0px #000, -3px  0px 0px #000, -3px -1px 0px #000, -2px -2px 0px #000, -1px -3px 0px #000,
                  3px  1px 0px #000,  2px  2px 0px #000,  1px  3px 0px #000,  0px  3px 0px #000, -1px  3px 0px #000, -2px  2px 0px #000, -3px  1px 0px #000,
                  3px -1px 0px #000,  2px -2px 0px #000,  1px -3px 0px #000,  0px -3px 0px #000, -1px -3px 0px #000, -2px -2px 0px #000, -3px -1px 0px #000
                 !important;
    font-size: 18px
    }
  .chat-line__timestamp {
    font-size: 12px
    }
  .chat-room__content {
    background-color: #00f !important;
    }
` );
