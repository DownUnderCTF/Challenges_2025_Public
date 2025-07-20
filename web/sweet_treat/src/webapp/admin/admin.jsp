<%@ page import="java.sql.*" %>
<%@ page import="java.util.*" %>
<%
    // Only allow admin access
    String adminUser = (String) session.getAttribute("user");
    if (adminUser == null || !"admin".equals(adminUser)) {
        response.sendRedirect("/index.jsp");
        return;
    }

    // Store sessions in application scope for management
    ServletContext appCtx = application;
    Map<String, HttpSession> sessionMap = (Map<String, HttpSession>) appCtx.getAttribute("sessionMap");
    if (sessionMap == null) {
        sessionMap = new HashMap<>();
        appCtx.setAttribute("sessionMap", sessionMap);
    }
    sessionMap.put(session.getId(), session);

    String dbURL = "jdbc:sqlite:/opt/directory.db";
    String action = request.getParameter("action");
    String message = null;

    // Clean up invalid sessions from the sessionMap before any operation
    Iterator<Map.Entry<String, HttpSession>> it = sessionMap.entrySet().iterator();
    while (it.hasNext()) {
        Map.Entry<String, HttpSession> entry = it.next();
        try {
            entry.getValue().getAttribute("user"); // Access to check if valid
        } catch (IllegalStateException ise) {
            it.remove(); // Remove invalidated session from map
        }
    }

    // Handle admin actions
    if ("reset_sessions".equals(action)) {
        // Invalidate all sessions and collect users before invalidation
        List<String> usersToKeep = new ArrayList<>();
        for (Map.Entry<String, HttpSession> entry : sessionMap.entrySet()) {
            HttpSession s = entry.getValue();
            String user = null;
            try {
                user = (String) s.getAttribute("user");
            } catch (IllegalStateException ise) {
                continue; // Skip already invalidated sessions
            }
            if (user != null) usersToKeep.add(user);
        }
        // Now invalidate all sessions
        for (Map.Entry<String, HttpSession> entry : sessionMap.entrySet()) {
            try {
                entry.getValue().invalidate();
            } catch (IllegalStateException ise) {
                // Already invalidated, skip
            }
        }
        sessionMap.clear();
        // Rebuild sessions for users
        for (String user : usersToKeep) {
            HttpSession newSession = request.getSession(true);
            newSession.setAttribute("user", user);
            sessionMap.put(newSession.getId(), newSession);
        }
        message = "All sessions have been reset and users remain logged in.";
    } else if ("kill_sessions".equals(action)) {
        for (Map.Entry<String, HttpSession> entry : sessionMap.entrySet()) {
            try {
                entry.getValue().invalidate();
            } catch (IllegalStateException ise) {
                // Already invalidated, skip
            }
        }
        sessionMap.clear();
        message = "All user sessions have been killed.";
    } else if ("delete_user".equals(action)) {
        String delUser = request.getParameter("username");
        if (delUser != null && !"admin".equals(delUser)) {
            try {
                Class.forName("org.sqlite.JDBC");
                Connection conn = DriverManager.getConnection(dbURL);
                PreparedStatement pstmt = conn.prepareStatement("DELETE FROM users WHERE username = ?");
                pstmt.setString(1, delUser);
                pstmt.executeUpdate();
                pstmt.close();
                conn.close();
                message = "User '" + delUser + "' deleted.";
            } catch(Exception e) {
                message = "Error deleting user: " + e.getMessage();
            }
        }
    } else if ("add_user".equals(action)) {
        String newUser = request.getParameter("new_username");
        String newPass = request.getParameter("new_password");
        if (newUser != null && newPass != null) {
            try {
                Class.forName("org.sqlite.JDBC");
                Connection conn = DriverManager.getConnection(dbURL);
                PreparedStatement pstmt = conn.prepareStatement("INSERT INTO users (username, password) VALUES (?, ?)");
                pstmt.setString(1, newUser);
                pstmt.setString(2, newPass);
                pstmt.executeUpdate();
                pstmt.close();
                conn.close();
                message = "User '" + newUser + "' added.";
            } catch(Exception e) {
                message = "Error adding user: " + e.getMessage();
            }
        }
    } else if ("update_user".equals(action)) {
        String updUser = request.getParameter("upd_username");
        String updPass = request.getParameter("upd_password");
        String updNewUser = request.getParameter("upd_new_username");
        // Prevent updating username for the currently logged in user
        if (updUser != null && (updPass != null || updNewUser != null)) {
            if (updNewUser != null && !updNewUser.isEmpty() && updUser.equals(adminUser)) {
                message = "You cannot update your own username while logged in.";
            } else if (updNewUser != null && !updNewUser.isEmpty()) {
                // Check if new username already exists
                boolean exists = false;
                try {
                    Class.forName("org.sqlite.JDBC");
                    Connection conn = DriverManager.getConnection(dbURL);
                    PreparedStatement checkStmt = conn.prepareStatement("SELECT 1 FROM users WHERE username = ?");
                    checkStmt.setString(1, updNewUser);
                    ResultSet checkRs = checkStmt.executeQuery();
                    if (checkRs.next()) {
                        exists = true;
                    }
                    checkRs.close();
                    checkStmt.close();
                    conn.close();
                } catch(Exception e) {
                    message = "Error checking username: " + e.getMessage();
                }
                if (exists) {
                    message = "Username '" + updNewUser + "' already exists. Please choose another.";
                } else {
                    try {
                        Class.forName("org.sqlite.JDBC");
                        Connection conn = DriverManager.getConnection(dbURL);
                        if (updPass != null && !updPass.isEmpty()) {
                            PreparedStatement pstmt = conn.prepareStatement("UPDATE users SET password = ? WHERE username = ?");
                            pstmt.setString(1, updPass);
                            pstmt.setString(2, updUser);
                            pstmt.executeUpdate();
                            pstmt.close();
                        }
                        PreparedStatement pstmt = conn.prepareStatement("UPDATE users SET username = ? WHERE username = ?");
                        pstmt.setString(1, updNewUser);
                        pstmt.setString(2, updUser);
                        pstmt.executeUpdate();
                        pstmt.close();
                        conn.close();
                        message = "User '" + updUser + "' updated.";
                    } catch(Exception e) {
                        message = "Error updating user: " + e.getMessage();
                    }
                }
            } else {
                try {
                    Class.forName("org.sqlite.JDBC");
                    Connection conn = DriverManager.getConnection(dbURL);
                    if (updPass != null && !updPass.isEmpty()) {
                        PreparedStatement pstmt = conn.prepareStatement("UPDATE users SET password = ? WHERE username = ?");
                        pstmt.setString(1, updPass);
                        pstmt.setString(2, updUser);
                        pstmt.executeUpdate();
                        pstmt.close();
                    }
                    conn.close();
                    message = "User '" + updUser + "' updated.";
                } catch(Exception e) {
                    message = "Error updating user: " + e.getMessage();
                }
            }
        }
    }

    // Fetch all users for display
    List<Map<String, String>> users = new ArrayList<>();
    try {
        Class.forName("org.sqlite.JDBC");
        Connection conn = DriverManager.getConnection(dbURL);
        PreparedStatement pstmt = conn.prepareStatement("SELECT username FROM users");
        ResultSet rs = pstmt.executeQuery();
        while (rs.next()) {
            Map<String, String> user = new HashMap<>();
            user.put("username", rs.getString("username"));
            users.add(user);
        }
        rs.close();
        pstmt.close();
        conn.close();
    } catch(Exception e) {
        message = "Error fetching users: " + e.getMessage();
    }

%>
<%! 
    public String escapeHtml(String s) {
        if (s == null) return "";
        return s.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&#x27;");
    }
%>
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <link rel="stylesheet" href="/styles.css">
    <style>
        .user-list, .user-list-admin, .report-list, .admin-user-list {
            list-style-type: none !important;
            list-style: none !important;
            padding-left: 0 !important;
            margin: 0 !important;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/index.jsp">Home</a>
        <a href="/edit_profile.jsp">Edit Profile</a>
        <a href="/admin/admin-review.jsp">Review Reports</a>
        <a href="/admin/admin.jsp">Admin Dashboard</a>
        <a href="/logout.jsp">Logout</a>
    </div>
    <div class="admin-container">
        <h2>Admin Panel</h2>
        <% if (message != null) { %>
            <div class="msg"><%= escapeHtml(message) %></div>
        <% } %>
        <div class="section">
            <form method="post">
                <button name="action" value="reset_sessions" type="submit">Reset All Sessions (Keep Users Logged In)</button>
                <button name="action" value="kill_sessions" type="submit" style="background:#b91c1c;">Kill All User Sessions</button>
            </form>
        </div>
        <div class="section">
            <h3>Users</h3>
            <ul class="user-list">
                <% for (Map<String, String> user : users) { %>
                    <li>
                        <%= escapeHtml(user.get("username")) %>
                        <% if (!"admin".equals(user.get("username"))) { %>
                            <form method="post" style="display:inline;">
                                <input type="hidden" name="username" value="<%= escapeHtml(user.get("username")) %>"/>
                                <button name="action" value="delete_user" type="submit" style="background:#b91c1c;">Delete</button>
                            </form>
                        <% } %>
                    </li>
                <% } %>
            </ul>
        </div>
        <div class="section">
            <h3>Add User</h3>
            <form method="post">
                <label>Username:</label><br>
                <input type="text" name="new_username" required><br>
                <label>Password:</label><br>
                <input type="password" name="new_password" required><br>
                <button name="action" value="add_user" type="submit">Add User</button>
            </form>
        </div>
        <div class="section">
            <h3>Update User</h3>
            <form method="post">
                <label>Current Username:</label><br>
                <input type="text" name="upd_username" required><br>
                <label>New Username (optional):</label><br>
                <input type="text" name="upd_new_username"><br>
                <label>New Password (optional):</label><br>
                <input type="password" name="upd_password"><br>
                <button name="action" value="update_user" type="submit">Update User</button>
            </form>
        </div>
    </div>
    <footer>
      <p style="text-align: center; font-size: 0.9rem; color: #6b7280;">&copy; 2025 Sweet Treats INC</p>
      <p style="text-align: center; font-size: 0.8rem; color: #9ca3af;">For internal use only</p>
    </footer>
</body>
</html>
