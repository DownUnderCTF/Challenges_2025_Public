<%@ page import="java.sql.*" %>
<%
    // Require user to be signed in
    if (session.getAttribute("user") == null) {
        response.sendRedirect("/index.jsp");
        return;
    }
    String username = (String) session.getAttribute("user");
    String dbURL = "jdbc:sqlite:/opt/directory.db";
    Connection conn = null;
    PreparedStatement pstmt = null;
    ResultSet rs = null;
    String aboutMe = "";
    String lang = "en";
    Cookie[] cookies = request.getCookies();
    if (cookies != null) {
        for (Cookie c : cookies) {
            if ("language".equals(c.getName())) {
                lang = c.getValue();
            }
        }
    }

    // Handle form submission for updating about me
    if ("POST".equalsIgnoreCase(request.getMethod()) && request.getParameter("aboutMe") != null) {
        String newAboutMe = request.getParameter("aboutMe");
        try {
            Class.forName("org.sqlite.JDBC");
            conn = DriverManager.getConnection(dbURL);

            String updateSql = "UPDATE users SET aboutme = ? WHERE username = ?";
            pstmt = conn.prepareStatement(updateSql);
            pstmt.setString(1, newAboutMe);
            pstmt.setString(2, username);
            pstmt.executeUpdate();
            pstmt.close();
        } catch(Exception e) {
            out.println("Database error: " + e.getMessage());
        } finally {
            try { if (pstmt != null) pstmt.close(); } catch(Exception e) {}
            try { if (conn != null) conn.close(); } catch(Exception e) {}
        }
    }

    // Handle report profile to admin
    if ("POST".equalsIgnoreCase(request.getMethod()) && request.getParameter("reportProfile") != null) {
        try {
            Class.forName("org.sqlite.JDBC");
            conn = DriverManager.getConnection(dbURL);

            String insertReport = "INSERT INTO Reports (username) VALUES (?)";
            pstmt = conn.prepareStatement(insertReport);
            pstmt.setString(1, username);
            pstmt.executeUpdate();
            pstmt.close();
        } catch(Exception e) {
            out.println("Database error: " + e.getMessage());
        } finally {
            try { if (pstmt != null) pstmt.close(); } catch(Exception e) {}
            try { if (conn != null) conn.close(); } catch(Exception e) {}
        }
        try {
            java.net.URL url = new java.net.URL("http://127.0.0.1:8000/visit");
            java.net.HttpURLConnection con = (java.net.HttpURLConnection) url.openConnection();
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json");
            con.setRequestProperty("X-SSRF-Protection", "1");
            con.setDoOutput(true);
            String json = "{\"url\": \"http://127.0.0.1:8080/admin/admin-review.jsp\"}";
            try (java.io.OutputStream os = con.getOutputStream()) {
                byte[] input = json.getBytes("utf-8");
                os.write(input, 0, input.length);
            }
            int code = con.getResponseCode();
            // Optionally, you can read the response here if needed
            if (code != 202) {
                out.println("Error notifying bot: " + code);
            } else {
                out.println("Bot notified successfully.");
            }
            con.disconnect();
        } catch(Exception e) {
            out.println("Bot notify error: " + e.getMessage());
        }
    }

    // Fetch current aboutme section for this user
    try {
        Class.forName("org.sqlite.JDBC");
        conn = DriverManager.getConnection(dbURL);
        String selectSql = "SELECT aboutme FROM users WHERE username = ?";
        pstmt = conn.prepareStatement(selectSql);
        pstmt.setString(1, username);
        rs = pstmt.executeQuery();
        if (rs.next()) {
            aboutMe = rs.getString("aboutme");
            if (aboutMe == null) aboutMe = "";
        }
    } catch(Exception e) {
        out.println("Database error: " + e.getMessage());
    } finally {
        try { if (rs != null) rs.close(); } catch(Exception e) {}
        try { if (pstmt != null) pstmt.close(); } catch(Exception e) {}
        try { if (conn != null) conn.close(); } catch(Exception e) {}
    }
    String loggedInUser = (String) session.getAttribute("user");
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
    <title>Edit Profile</title>
    <style>
        .navbar {
            width: 100%;
            background: #2563eb;
            color: #fff;
            padding: 0.7rem 0;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 1.5rem;
            position: fixed;
            top: 0;
            left: 0;
            z-index: 200;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .navbar a {
            color: #fff;
            text-decoration: none;
            font-weight: 500;
            font-size: 1rem;
            margin-right: 2rem;
            transition: color 0.2s;
        }
        .navbar a:hover {
            color: #c7d2fe;
        }
        .user-bar {
            position: absolute;
            top: 70px;
            right: 32px;
            background: #f4f6fb;
            color: #2d3a4b;
            padding: 0.5rem 1.2rem;
            border-radius: 20px;
            font-weight: 500;
            font-size: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            z-index: 100;
        }
        .profile-container {
            background: #fff;
            padding: 2.5rem 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
            width: 400px;
            margin: 110px auto 0 auto;
            text-align: center;
        }
        textarea {
            width: 100%;
            padding: 0.7rem;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 1rem;
            background: #f9fafb;
            margin-bottom: 1.2rem;
            resize: vertical;
        }
        button {
            padding: 0.8rem 2rem;
            background: #4f8cff;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #2563eb;
        }
        .report-btn {
            margin-top: 1.2rem;
            background: #ff4f4f;
            color: #fff;
        }
        .report-btn:hover {
            background: #c53030;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/index.jsp">Home</a>
        <a href="/edit_profile.jsp">Edit Profile</a>
        <% if ("admin".equals(loggedInUser)) { %>
            <a href="/admin/admin-review.jsp">Review Reports</a>
            <a href="/admin/admin.jsp">Admin Dashboard</a>
        <% } %>
        <a href="/logout.jsp">Logout</a>
    </div>
    <div class="user-bar">
        <span>👤 <%= escapeHtml(username) %></span>
    </div>
    <div class="profile-container">
        <h2>Edit Your About Me</h2>
        <form method="POST">
            <textarea name="aboutMe" rows="8" placeholder="Write something about yourself..."><%= aboutMe != null ? escapeHtml(aboutMe) : "" %></textarea>
            <br>
            <button type="submit">Save</button>
        </form>
        <form method="POST" style="margin-top: 0;">
            <input type="hidden" name="reportProfile" value="1" />
            <button type="submit" class="report-btn">Report Profile to Admin</button>
        </form>
    </div>
    <footer>
      <p style="text-align: center; font-size: 0.9rem; color: #6b7280;">&copy; 2025 Sweet Treats INC</p>
      <p style="text-align: center; font-size: 0.8rem; color: #9ca3af;">For internal use only</p>
    </footer>
</body>
</html>
