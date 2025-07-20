import "./App.css";
import CharGridInput from "./CharGridInput";
import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

function App() {
  const [ptChars, setPTChars] = useState(["D", "U", "C", "T", "F", "{"]);
  const [ctBlocks, setCTBlocks] = useState([]);
  const [locked, setLocked] = useState(false);
  const [bruteIndex, setBruteIndex] = useState(null);
  const [lastBruteIndex, setLastBruteIndex] = useState(null);
  const [showFlagGhost, setShowFlagGhost] = useState(true);
  const [focused, setFocused] = useState(false);

  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const encodeAndSplit = (b64data) => {
    const raw = atob(b64data);
    const blocks = [];
    for (let i = 0; i < raw.length; i += 16) {
      blocks.push(btoa(raw.slice(i, i + 16)).replace(/=+$/, ""));
    }
    return blocks;
  };

  const submitSingle = async (plaintext) => {
    const fetchPromise = fetch(window.location + "encrypt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: btoa(plaintext) }),
    });

    const [res] = await Promise.all([fetchPromise]);
    const data = await res.json();
    const blocks = encodeAndSplit(data["ciphertext"]);
    setCTBlocks([blocks]);
  };

  const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

  const submitBatch = async (plaintext, index) => {
    const batch = Array.from(charset).map((char) => {
      const chars = plaintext.split("");
      chars[index] = char;
      return btoa(chars.join(""));
    });

    const fetchPromise = fetch(window.location + "encrypt_batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: batch }),
    });

    const [res] = await Promise.all([fetchPromise]);
    const data = await res.json();
    setCTBlocks(data["ciphertexts"].map(encodeAndSplit));
  };

  const submitText = async () => {
    const plaintext = ptChars.join("");

    setShowFlagGhost(true);
    setLocked(true);
    try {
      if (bruteIndex == null || bruteIndex >= plaintext.length) {
        await submitSingle(plaintext);
      } else {
        await submitBatch(plaintext, bruteIndex);
        setLastBruteIndex(bruteIndex);
      }
    } catch (e) {
    } finally {
      setLocked(false);
    }
  };

  const helpModal = (
    <>
      <label htmlFor="modal" className="m-4 btn btn-secondary">
        Help
      </label>
      <input type="checkbox" id="modal" className="modal-toggle" />
      <div className="modal">
        <div className="modal-box w-full max-w-4xl">
          <h2 className="font-bold text-lg">Help</h2>
          <p className="py-4">
            The <i>ECB-A-TRON 9000</i> appends a secret phrase to your input
            before encrypting. Can you abuse this somehow and recover the
            secret?
          </p>

          <p>
            Wrap the secret phrase like this:
            <code className="bg-base-300 text-base-content font-mono px-1 rounded">
              DUCTF&#123;&lt;secret phrase&gt;&#125;
            </code>
            for the flag
          </p>

          <h3 className="mt-4 font-bold">Controls</h3>
          <table className="table w-full">
            <thead>
              <tr>
                <th>Action</th>
                <th>Keyboard</th>
                <th>Mouse</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th>Move Cursor</th>
                <td>Left/Right Arrows</td>
                <td>Left Click</td>
              </tr>
              <tr>
                <th>Insert Character</th>
                <td>A-Z</td>
                <td>-</td>
              </tr>
              <tr>
                <th>Delete Character</th>
                <td>Backspace</td>
                <td>-</td>
              </tr>
              <tr>
                <th>Clear Input</th>
                <td>Del</td>
                <td>-</td>
              </tr>
              <tr>
                <th>Toggle Brute Force Mode</th>
                <td>Tab</td>
                <td>Right Click</td>
              </tr>
            </tbody>
          </table>
          <h3 className="mt-4 font-bold">Hints</h3>
          <ul className="mt-2 list-disc list-inside space-y-2">
            <li>
              To get you started, have a look at
              <a href="https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Electronic_codebook_(ECB)">
                {" "}
                <u>this page</u>
              </a>
            </li>
            <li>
              The secret phrase consists of only capital English characters.
            </li>
            <li>
              If the plaintext length isn't divisible by 16, it is padded with
              space (0x20) characters.
            </li>
            <li>
              Use <i>brute force mode</i> if you need to repeat many requests
              for a single position!
            </li>
          </ul>
          <div className="modal-action">
            <label htmlFor="modal" className="btn">
              Back
            </label>
          </div>
        </div>
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-base-100 text-base-content flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold mb-6">ECB-A-TRON 9000</h1>

      <div
        tabIndex={0}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
      >
        <CharGridInput
          ptChars={ptChars}
          setPTChars={setPTChars}
          maxLength={16}
          locked={locked}
          submitText={submitText}
          ctBlocks={ctBlocks}
          bruteIndex={bruteIndex}
          setBruteIndex={setBruteIndex}
          lastBruteIndex={lastBruteIndex}
          showFlagGhost={showFlagGhost}
          focused={focused}
        />
      </div>
      <div className="flex flex-row">
        <button className="m-4 btn btn-primary" onClick={submitText}>
          Encrypt
        </button>
        {helpModal}
      </div>
    </div>
  );
}

export default App;
