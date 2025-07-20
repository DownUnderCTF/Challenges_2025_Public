<%@ page import="java.sql.*" %>
<%
  String lang = "en";
  Cookie[] cookies = request.getCookies();
  if (cookies != null) {
      for (Cookie c : cookies) {
          if ("language".equals(c.getName())) {
              lang = c.getValue();
          }
      }
  }
  String loggedInUser = (String) session.getAttribute("user");

  // Fetch all users
  String dbURL = "jdbc:sqlite:/opt/directory.db";
  Connection conn = null;
  PreparedStatement pstmt = null;
  ResultSet rs = null;
  java.util.List<String> usernames = new java.util.ArrayList<>();
  try {
      Class.forName("org.sqlite.JDBC");
      conn = DriverManager.getConnection(dbURL);
      String sql = "SELECT username FROM users";
      pstmt = conn.prepareStatement(sql);
      rs = pstmt.executeQuery();
      while (rs.next()) {
          usernames.add(rs.getString("username"));
      }
  } catch(Exception e) {
      out.println("Database error: " + e.getMessage());
  } finally {
      try { if (rs != null) rs.close(); } catch(Exception e) {}
      try { if (pstmt != null) pstmt.close(); } catch(Exception e) {}
      try { if (conn != null) conn.close(); } catch(Exception e) {}
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
<html lang="<%= lang %>">
  <head>
    <title>Directory Application - Users</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="/styles.css">
  </head>
  <body>
    <div class="navbar">
      <% if (loggedInUser != null) { %>
        <a href="/index.jsp">Home</a>
        <a href="/edit_profile.jsp">Edit Profile</a>
        <% if ("admin".equals(loggedInUser)) { %>
          <a href="/admin/admin-review.jsp">Review Reports</a>
          <a href="/admin/admin.jsp">Admin Dashboard</a>
        <% } %>
        <a href="/logout.jsp">Logout</a>
      <% } else { %>
        <a href="/index.jsp">Home</a>
        <a href="/login.jsp">Login</a>
        <a href="/register.jsp">Register</a>
      <% } %>
    </div>
    <div class="directory-title">Directory Application</div>
    <div class="user-list-container">
      <h2>Users</h2>
      <ul class="user-list">
        <% for (String user : usernames) { %>
          <li><%= escapeHtml(user) %></li>
        <% } %>
      </ul>
    </div>
    <div class="footer">
      <p style="text-align: center; font-size: 0.9rem; color: #6b7280;">&copy; 2025 Sweet Treats INC</p>
      <p style="text-align: center; font-size: 0.8rem; color: #9ca3af;">For internal use only</p>
    </div>
  </body>
</html>

<style>
/* Hide bullets for all user/admin lists */
.user-list, .user-list-admin, .report-list, .admin-user-list {
    list-style-type: none !important;
    list-style: none !important;
    padding-left: 0 !important;
    margin: 0 !important;
}

/* Center and style the directory title */
.directory-title {
    font-size: 2.4rem;
    color: #2d3a4b;
    margin: 3.5rem 0 2.5rem 0;
    letter-spacing: 1px;
    text-align: center;
    font-weight: 700;
    line-height: 1.2;
}
</style>