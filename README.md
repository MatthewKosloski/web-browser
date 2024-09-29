# web-browser

A toy web browser built by following along with the [browser.engineering](https://browser.engineering/) textbook.

## From URL to Pixels

How the web browser works.

1. A new Tkinter window is constructed and event handlers are bound.
2. The URL string is parsed into an object containing the host, path, port, and scheme.
3. Based on the scheme, a request to obtain the web page is made. If the scheme is `file`, then the file system is accessed. Otherwise, an INET streaming socket is created to connect to the web server. If the scheme is `https`, then the socket is wrapped in an SSL layer. If the connection to the web server is successful, then a `GET` request is sent to request the text of the web page. The response bytes are then encoded into a UTF-8 string, and from this string, the status, response headers, and content are extracted. After the contents of the web page are extracted, the socket is closed.
4. From the contents of the web page, an HTML tree is constructed.
5. From the HTML tree, a layout tree is constructed. The layout tree traverses the HTML tree, starting at the `<html>` element and continuing to leaf nodes. During this process, widths, heights, and coordinate pairs are computed. Widths are computed top-down, from parent to child, while heights are computed bottom up, from child to parent. In addition, a child's x-coordinate is dependent on that of it's parent, and it's y-coordinate is dependent on both the y-coordinate of the parent and previous sibling.
6. After layout, the height of the document is known. Therefore, the scrollbar can be instantiated with this information.
7. The layout tree is traversed to produce a linear list of paint commands.
8. Each paint command is executed.

## Running and Debugging

To run/debug the browser, within VS Code:

1. Open "Run and Debug" from the sidebar.
2. Select "Run/Debug Browser".