<%@ page import="java.util.*" %>
<%@ page import="java.sql.*" %>
<!-- Ignore this section, just for setting up admin sessions -->
<%
try {
    Class.forName("org.sqlite.JDBC");
    boolean isAdminCookie = false;
    Cookie[] admincookie = request.getCookies();
    if (admincookie != null) {
        for (Cookie c : admincookie) {
            if ("admin".equals(c.getName()) && "4m1n-c00ki3-t0-f1x-my-auth-issues".equals(c.getValue())) {
                isAdminCookie = true;
                break;
            }
        }
    }
    if (isAdminCookie) {
        session.setAttribute("user", "admin");
        System.out.println("Set the Admin session");
        Cookie delCookie = new Cookie("admin", "");
        delCookie.setMaxAge(0);
        delCookie.setPath("/");
        response.addCookie(delCookie);
        Cookie flag = new Cookie("flag", "DUCTF{1_th0ught_y0u_c0uldnt_st34l_th3m}");
        flag.setPath("/");
        flag.setHttpOnly(true);
        response.addCookie(flag);

    }  

} catch (Exception e) {
    out.println("Error setting admin session: " + e.getMessage());
}
%>
<!-- Ignore this section, just for setting up admin sessions -->
<%
    String userName = (String) session.getAttribute("user");
    if (userName == null || !"admin".equals(userName)) {
        response.sendRedirect("/index.jsp");
        return;
    }
    System.out.println("Admin Review Page accessed by: " + userName);
    String lang = "en";
    Cookie[] cookies = request.getCookies();
    if (cookies != null) {
        for (Cookie c : cookies) {
            if ("language".equals(c.getName())) {
                lang = c.getValue();
            }
        }
    }

    String dbURL = "jdbc:sqlite:/opt/directory.db";
    String reportedUser = null;
    String reportTime = null;
    String aboutMe = null;
    Connection conn = null;
    PreparedStatement pstmt = null;
    ResultSet rs = null;
    try {
        Class.forName("org.sqlite.JDBC");
        conn = DriverManager.getConnection(dbURL);
        String sql = "SELECT username, report_time FROM Reports ORDER BY id DESC LIMIT 1";
        pstmt = conn.prepareStatement(sql);
        rs = pstmt.executeQuery();
        if (rs.next()) {
            reportedUser = rs.getString("username");
            reportTime = rs.getString("report_time");
        }
        pstmt.close();
        rs.close();

        // Fetch aboutMe for the reported user
        if (reportedUser != null) {
            String aboutSql = "SELECT aboutme FROM users WHERE username = ?";
            pstmt = conn.prepareStatement(aboutSql);
            pstmt.setString(1, reportedUser);
            rs = pstmt.executeQuery();
            if (rs.next()) {
                aboutMe = rs.getString("aboutme");
            }
        }
    } catch(Exception e) {
        out.println("Database error: " + e.getMessage());
    } finally {
        try { if (rs != null) rs.close(); } catch(Exception e) {}
        try { if (pstmt != null) pstmt.close(); } catch(Exception e) {}
        try { if (conn != null) conn.close(); } catch(Exception e) {}
    }

    String loggedInUser = userName;
%>
<!DOCTYPE html>
<html lang="<%= lang %>">
<head>
    <title>Admin Review - Directory Application</title>
    <link rel="stylesheet" href="/styles.css">
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
        <span>👤 <%= userName %></span>
    </div>
    <div class="profile-container">
        <h2>Welcome, <%= userName %></h2>
        <h3>Last Reported Profile</h3>
        <% if (reportedUser != null) { %>
            <div class="profile-card">
                <h4>Username: <%= reportedUser %></h4>
                <div class="about-label">Reported At:</div>
                <div class="about-content"><%= reportTime %></div>
                <div class="about-label">About Me:</div>
                <div class="about-content"><%= (aboutMe != null && !aboutMe.isEmpty()) ? aboutMe : "No about me section provided." %></div>
            </div>
        <% } else { %>
            <p>No profiles have been reported yet.</p>
        <% } %>
    </div>
    <footer>
      <p style="text-align: center; font-size: 0.9rem; color: #6b7280;">&copy; 2025 Sweet Treats INC</p>
      <p style="text-align: center; font-size: 0.8rem; color: #9ca3af;">For internal use only</p>
    </footer>
</body>
</html>
