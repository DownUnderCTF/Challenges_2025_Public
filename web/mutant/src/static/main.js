const inp = new URLSearchParams(location.search).get("input");

// Reporting stuff
reportbtn.addEventListener('click', () => {
  fetch("/report", {
    method: "POST",
    body: inp
  }).then(r => alert("Successfully reported")).catch(alert);
});

// Challenge
mytextarea.value = inp;

console.log("Original", inp);

const t = document.createElement("template");
t.innerHTML = inp;

console.log("After injecting into template", t.innerHTML);

const nodes = [t.content];
while (nodes.length > 0) {
  const n = nodes.pop();

  console.log("Parsed element", n.outerHTML);

  if (n.attributes) {
    while (n.attributes.length > 0) {
      n.removeAttribute(n.attributes[0].name);
    }
  }

  // Fix XSS reported by our bug bounty community
  if (n.nodeName !== "#document-fragment" && (n.nodeName.length === 6 || n.nodeName.length === 8)) {
    n.parentNode.removeChild(n);
    continue;
  }
  
  for (let i = n.children.length - 1; i >= 0; i--) {
    nodes.push(n.children[i]);
  }
}

console.log("After sanitization", t.innerHTML);

myoutputdebug.innerText = t.innerHTML;
myoutput.innerHTML = t.innerHTML;

console.log("Final", myoutput.innerHTML);
