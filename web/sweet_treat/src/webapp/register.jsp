<%@ page import="java.sql.*" %>
<%
    String dbURL = "jdbc:sqlite:/opt/directory.db";
    String errorMsg = "";
    String successMsg = "";
    if ("POST".equalsIgnoreCase(request.getMethod())) {
        String username = request.getParameter("username");
        String password = request.getParameter("password");
        String firstname = request.getParameter("firstname");
        String lastname = request.getParameter("lastname");
        String organisation = request.getParameter("organisation");
        if (username == null || password == null || username.trim().isEmpty() || password.trim().isEmpty()) {
            errorMsg = "Username and password are required.";
        } else {
            Connection conn = null;
            PreparedStatement pstmt = null;
            ResultSet rs = null;
            try {
                Class.forName("org.sqlite.JDBC");
                conn = DriverManager.getConnection(dbURL);
                // Check if username already exists
                String checkSql = "SELECT username FROM users WHERE username = ?";
                pstmt = conn.prepareStatement(checkSql);
                pstmt.setString(1, username);
                rs = pstmt.executeQuery();
                if (rs.next()) {
                    errorMsg = "Username already exists.";
                } else {
                    pstmt.close();
                    // Insert new user
                    String insertSql = "INSERT INTO users (username, password, firstname, lastname, organisation) VALUES (?, ?, ?, ?, ?)";
                    pstmt = conn.prepareStatement(insertSql);
                    pstmt.setString(1, username);
                    pstmt.setString(2, password);
                    pstmt.setString(3, firstname);
                    pstmt.setString(4, lastname);
                    pstmt.setString(5, organisation);
                    pstmt.executeUpdate();
                    successMsg = "Registration successful! You can now <a href='/login.jsp'>login</a>.";
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
    String loggedInUser = (String) session.getAttribute("user");
%>
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Register - Directory Application</title>
    <link rel="stylesheet" href="/styles.css">
</head>
<body>
    <div class="navbar">
        <a href="/index.jsp">Home</a>
        <% if (loggedInUser == null) { %>
            <a href="/login.jsp">Login</a>
            <a href="/register.jsp">Register</a>
        <% } else { %>
            <a href="/edit_profile.jsp">Edit Profile</a>
            <a href="/logout.jsp">Logout</a>
        <% } %>
    </div>
    <div class="login-container">
        <h2>Register</h2>
        <% if (!"".equals(errorMsg)) { %>
            <div class="msg" style="color: #c53030;"><%= errorMsg %></div>
        <% } %>
        <% if (!"".equals(successMsg)) { %>
            <div class="msg" style="color: #2563eb;"><%= successMsg %></div>
        <% } %>
        <form method="POST">
            <label for="username">Username</label>
            <input type="text" name="username" required autocomplete="off" />
            <label for="password">Password</label>
            <input type="password" name="password" required />
            <label for="firstname">First Name</label>
            <input type="text" name="firstname" />
            <label for="lastname">Last Name</label>
            <input type="text" name="lastname" />
            <label for="organisation">Organisation</label>
            <input type="text" name="organisation" />
            <button type="submit">Register</button>
        </form>
    </div>
    <footer>
      <p style="text-align: center; font-size: 0.9rem; color: #6b7280;">&copy; 2025 Sweet Treats INC</p>
      <p style="text-align: center; font-size: 0.8rem; color: #9ca3af;">For internal use only</p>
    </footer>
</body>
</html>