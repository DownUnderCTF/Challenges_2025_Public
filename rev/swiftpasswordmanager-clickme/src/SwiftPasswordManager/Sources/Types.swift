import Foundation

struct LoginEntry: Codable, Equatable, Identifiable {
  let id = UUID()
  var title: String
  var username: String
  var password: String
  var notes: String
  var createdAt: Date
  var modifiedAt: Date

  var truncatedUsername: String {
    if username.isEmpty { return "No username" }
    if username.count > 20 {
      return String(username.prefix(17)) + "..."
    }
    return username
  }
}

struct SPMFileHeader {
  static let magic: UInt32 = 0x314D5053
  let version: UInt16 = 1
  let flags: UInt16 = 0
  let salt: Data
  let nonce: Data
  let tagSize: UInt16
  let dataSize: UInt32
}

