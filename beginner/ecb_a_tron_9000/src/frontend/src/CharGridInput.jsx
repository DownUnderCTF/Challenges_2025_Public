import { useState, useEffect, useRef } from "react";

// single character cell
function CharBox({
  char,
  index,
  highlight,
  locked,
  alert,
  faded,
  setBruteIndex,
  safeSetCursorIndex,
}) {
  const onContextMenu = (e) => {
    e.preventDefault();
    if (locked) return;
    setBruteIndex((prev) => (prev === index ? null : index));
  };

  const base =
    "h-8 w-8 flex items-center justify-center border rounded border-gray-700 text-lg font-mono";

  const stateClass = (() => {
    if (highlight) return "ring-5 ring-blue-400";
    return "";
  })();

  const colorClass = (() => {
    if (locked) return "bg-gray-400 text-gray-600";
    if (faded) return "bg-red-100 text-red-400 opacity-60";
    if (alert) return "bg-green-300 text-black font-semibold";
    return "bg-white text-black";
  })();

  return (
    <div
      className={`${base} ${colorClass} ${stateClass}`}
      onContextMenu={onContextMenu}
      onClick={() => {
        safeSetCursorIndex(index);
      }}
    >
      {char ?? ""}
    </div>
  );
}

function BlockWrapper({ children }) {
  return <div className="p-2 border rounded-lg">{children}</div>;
}

// group of 16 cells
function CharBlock({
  group,
  offset,
  cursorIndex,
  locked,
  bruteIndex,
  setBruteIndex,
  ptLength,
  focused,
  safeSetCursorIndex,
}) {
  const charBoxes = Array.from({ length: 16 }).map((_, i) => {
    const currIndex = offset + i;
    return (
      <CharBox
        key={currIndex}
        char={group[i]}
        index={currIndex}
        highlight={focused && currIndex === cursorIndex}
        faded={group[i] && ptLength <= currIndex}
        alert={bruteIndex == currIndex}
        locked={locked || ptLength + 16 <= currIndex}
        setBruteIndex={setBruteIndex}
        safeSetCursorIndex={safeSetCursorIndex}
      />
    );
  });
  const children = <div className="flex flex-row gap-1">{charBoxes}</div>;
  return <BlockWrapper children={children} />;
}

// base64 text in rounded
function TextBlock({ text }) {
  const children = <div className="text-center select-text">{text} </div>;
  return <BlockWrapper children={children} />;
}

// full input component
export default function CharGridInput({
  ptChars,
  setPTChars,
  maxLength = 16,
  locked,
  submitText,
  ctBlocks,
  bruteIndex,
  setBruteIndex,
  lastBruteIndex,
  showFlagGhost,
  focused,
}) {
  const containerRef = useRef(null);
  const [cursorIndex, setCursorIndex] = useState(ptChars.length);

  if (bruteIndex !== null && ptChars.length <= bruteIndex) {
    setBruteIndex(null);
  }

  useEffect(() => {
    containerRef.current?.focus();
  }, []);

  const decrementCursor = (delta) =>
    setCursorIndex(Math.max(cursorIndex - delta, 0));
  const incrementCursor = (delta, limit = ptChars.length) =>
    setCursorIndex(
      Math.min(cursorIndex + delta, Math.min(limit, maxLength - 1)),
    );
  const safeSetCursorIndex = (newValue, limit = ptChars.length) => {
    setCursorIndex(
      Math.max(Math.min(newValue, Math.min(limit, maxLength - 1)), 0),
    );
  };

  const insertChar = (key) =>
    setPTChars((c) => {
      const left = c.slice(0, cursorIndex);
      const right = c.slice(cursorIndex + 1, c.length);
      const newPTChars = [...left, key, ...right];
      incrementCursor(1, newPTChars.length);
      return newPTChars;
    });

  const deleteChar = () => {
    setPTChars((c) => {
      const left = c.slice(0, cursorIndex);
      const right = c.slice(cursorIndex + 1, c.length);
      const newPTChars = [...left, ...right];
      decrementCursor(1);
      return newPTChars;
    });
  };

  const onKeyDown = (e) => {
    if (locked) return;
    const key = e.key;

    // do not block modifier keys
    if (e.ctrlKey || e.altKey || e.metaKey) {
      return;
    }

    if (
      key.length === 1 &&
      ptChars.length <= maxLength &&
      key.match(/[\x20-\x7E]/)
    ) {
      e.preventDefault();
      insertChar(key);
    } else if (key === "Backspace") {
      e.preventDefault();
      deleteChar();
    } else if (key === "Delete") {
      e.preventDefault();
      setPTChars([]);
      setCursorIndex(-1);
    } else if (key === "Enter") {
      e.preventDefault();
      submitText();
    } else if (key === "Home") {
      e.preventDefault();
      safeSetCursorIndex(0);
      // ..
    } else if (key === "End") {
      e.preventDefault();
      safeSetCursorIndex(Infinity);
      //  ..
    } else if (key === "Tab") {
      e.preventDefault();
      if (cursorIndex >= ptChars.length) {
        insertChar(" ");
      }
      setBruteIndex((prev) => (prev === cursorIndex ? null : cursorIndex));
    } else if (key === "ArrowLeft") {
      e.preventDefault();
      decrementCursor(1);
    } else if (key === "ArrowRight") {
      e.preventDefault();
      incrementCursor(1);
    }
  };

  const groups = [];

  // buffer = user input + placeholder for flag + padding
  const flagPlaceHolder = Array(16).fill("?");

  const bufferChars = showFlagGhost ? ptChars.concat(flagPlaceHolder) : ptChars;

  const visibleLength = Math.max(1, Math.ceil(bufferChars.length / 16));
  for (let i = 0; i < visibleLength; i++) {
    groups.push(bufferChars.slice(16 * i, 16 * i + 16));
  }

  const ctGroups = [];
  for (let j = 0; j < ctBlocks.length; j++) {
    const innerGroups = [];
    for (let i = 0; i < visibleLength; i++) {
      innerGroups.push(ctBlocks[j][i]);
    }
    ctGroups.push(innerGroups);
  }

  const indexIsInBlock = (bruteIndex, gi) => Math.floor(bruteIndex / 16) === gi;

  return (
    <div
      tabIndex={0}
      onKeyDown={onKeyDown}
      ref={containerRef}
      className="outline-none max-w-full"
      aria-label="plaintext input grid"
      role="textbox"
    >
      <div className="flex flex-row gap-4 max-w-full select-none whitespace-nowrap">
        {groups.map((group, gi) => (
          <div className="flex flex-col gap-4">
            <CharBlock
              key={gi}
              group={group}
              offset={gi * 16}
              cursorIndex={cursorIndex}
              locked={locked}
              bruteIndex={bruteIndex}
              setBruteIndex={setBruteIndex}
              ptLength={ptChars.length}
              focused={focused}
              safeSetCursorIndex={safeSetCursorIndex}
            />
            <div className="font-mono">
              {ctGroups.length > 0 && ctGroups[0][gi] && (
                <div className="flex flex-col justify-center items-center h-12">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-6 w-6 text-white-600"
                    fill="none"
                    viewBox="0 0 24 50"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M12 2v48m0 0l-6-6m6 6l6-6"
                    />
                  </svg>
                </div>
              )}
              {ctGroups.map(
                (ctGroup, cgi) =>
                  ctGroup[gi] &&
                  (cgi === 0 || indexIsInBlock(lastBruteIndex, gi)) && (
                    <TextBlock
                      className="mt-4 h-full"
                      text={`${ctGroups.length > 1 && indexIsInBlock(lastBruteIndex, gi) ? String.fromCharCode(cgi + 0x41) + ":" : ""} ${ctGroup[gi]}`}
                    />
                  ),
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
