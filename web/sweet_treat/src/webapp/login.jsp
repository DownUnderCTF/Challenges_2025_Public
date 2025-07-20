<%@ page import="java.util.*" %>
<%@ page import="java.sql.*" %>
<%
    String dbURL = "jdbc:sqlite:/opt/directory.db";
    String errorMsg = "";
    String loggedInUser = (String) session.getAttribute("user");

    if (loggedInUser != null) {
        response.sendRedirect("/index.jsp");
        return;
    }

    if ("POST".equalsIgnoreCase(request.getMethod())) {
        String username = request.getParameter("username");
        String password = request.getParameter("password");
        if (username == null || password == null || username.trim().isEmpty() || password.trim().isEmpty()) {
            errorMsg = "Username and password are required.";
        } else {
            Connection conn = null;
            PreparedStatement pstmt = null;
            ResultSet rs = null;
            try {
                Class.forName("org.sqlite.JDBC");
                conn = DriverManager.getConnection(dbURL);
                String sql = "SELECT username FROM users WHERE username = ? AND password = ?";
                pstmt = conn.prepareStatement(sql);
                pstmt.setString(1, username);
                pstmt.setString(2, password);
                rs = pstmt.executeQuery();
                if (rs.next()) {
                    session.setAttribute("user", username);
                    response.sendRedirect("/index.jsp");
                    return;
                } else {
                    errorMsg = "Invalid username or password.";
                }
            } catch(Exception e) {
                errorMsg = "Database error: " + e.getMessage();
            } finally {
                try { if (rs != null) rs.close(); } catch(Exception e) {}
                try { if (pstmt != null) pstmt.close(); } catch(Exception e) {}
                try { if (conn != null) conn.close(); } catch(Exception e) {}
            }
        }
    }
%>
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Login - Directory Application</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
    <div class="navbar">
        <a href="/index.jsp">Home</a>
        <a href="/login.jsp">Login</a>
        <a href="/register.jsp">Register</a>
    </div>
    <div class="login-container">
        <h2>Login</h2>
        <% if (!"".equals(errorMsg)) { %>
            <div class="msg" style="color: #c53030;"><%= errorMsg %></div>
        <% } %>
        <form method="POST">
            <label for="username">Username</label>
            <input type="text" name="username" required autocomplete="off" />
            <label for="password">Password</label>
            <input type="password" name="password" required />
            <button type="submit">Login</button>
        </form>
    </div>
    <div class="footer">
      <p style="text-align: center; font-size: 0.9rem; color: #6b7280;">&copy; 2025 Sweet Treats INC</p>
      <p style="text-align: center; font-size: 0.8rem; color: #9ca3af;">For internal use only</p>
    </div>
</body>
</html>
