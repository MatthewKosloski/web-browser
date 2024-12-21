# web-browser

A toy web browser built by following along with the [browser.engineering](https://browser.engineering/) textbook.

## From Startup to Pixels

How the web browser works.

1. A new Tkinter window and canvas are constructed.
2. The browser chrome is initialized. The chrome is every part of the browser that isn't the actual web page itself, namely the address bar, navigation buttons, tabs, etc.
3. Browser window events are bounded to callback functions.
4. The startup URL string is parsed into an object containing the host, path, port, and scheme.
5. A new browser tab with a JavaScript execution context is initialized.
6. Based on the URL scheme, a request to obtain the web page is made. If the scheme is `file`, then the file system is accessed. Otherwise, an INET streaming socket is created to connect to the web server. If the scheme is `https`, then the socket is wrapped in an SSL layer. If the connection to the web server is successful, then a `GET` request is sent to request the text of the web page. The response bytes are then encoded into a UTF-8 string, and from this string, the status, response headers, and content are extracted. After the contents of the web page are extracted, the socket is closed.
7. From the contents of the web page, an HTML tree is constructed.
8. Linked stylesheets are downloaded and those CSS rules are merged with the CSS rules in the user agent stylesheet, sorted in order by cascade priority. CSS rules in linked stylesheets override user agent CSS rules.
9. Linked scripts are downloaded and executed.
10. For each node in the HTML tree, for every CSS property, a value is computed.
    - For each inheritable CSS property, if the node has a parent, then the node inherits the value of the CSS property from the parent. Otherwise, the node gets the default value of the inheritable property.
    - For each matching CSS selector, for every CSS property in the rule, the node gets the value of the property.
    - For every CSS property in the node's `style` attribute, the node gets the value of the property.
11. From the HTML tree annotated with CSS, a layout tree is constructed by traversing the HTML tree, starting at the `<html>` element and continuing to leaf nodes. During this process, widths, heights, and coordinate pairs are computed. Widths are computed top-down, from parent to child, while heights are computed bottom up, from child to parent. In addition, a child's x-coordinate is dependent on that of it's parent, and it's y-coordinate is dependent on both the y-coordinate of the parent and previous sibling.
12. At this point, the height of the web document is known, therefore, the scrollbar is initialized with this information.
13. The layout tree is traversed to produce a linear list of paint commands.
14. Each paint command is executed.
15. Steps 10-14 are repeated whenever JavaScript modifies the web page.

## Running and Debugging

To run/debug the browser, within VS Code:

1. Open "Run and Debug" from the sidebar.
2. Select "Run/Debug Browser".