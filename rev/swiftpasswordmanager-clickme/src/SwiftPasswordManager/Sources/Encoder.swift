import Foundation

class BinaryEncoder {
  private var data = Data()

  func encode<T: FixedWidthInteger>(_ value: T) {
    withUnsafeBytes(of: value.littleEndian) { bytes in
      data.append(contentsOf: bytes)
    }
  }

  func encode(_ string: String) {
    let utf8Data = string.data(using: .utf8) ?? Data()
    encode(UInt32(utf8Data.count))
    data.append(utf8Data)
  }

  func encode(_ date: Date) {
    encode(Int64(date.timeIntervalSince1970))
  }

  func encode(_ uuid: UUID) {
    let (u1, u2, u3, u4, u5, u6, u7, u8, u9, u10, u11, u12, u13, u14, u15, u16) = uuid.uuid
    data.append(contentsOf: [u1, u2, u3, u4, u5, u6, u7, u8, u9, u10, u11, u12, u13, u14, u15, u16])
  }

  func encode(_ entry: LoginEntry) {
    encode(entry.id)
    encode(entry.title)
    encode(entry.username)
    encode(entry.password)
    encode(entry.notes)
    encode(entry.createdAt)
    encode(entry.modifiedAt)
  }

  func encode(_ entries: [LoginEntry]) {
    encode(UInt32(entries.count))
    for entry in entries {
      encode(entry)
    }
  }

  func finalize() -> Data {
    return data
  }
}

// class BinaryDecoder {
//   private var data: Data
//   private var offset = 0
//
//   init(data: Data) {
//     self.data = data
//   }
//
//   func decode<T: FixedWidthInteger>(_ type: T.Type) throws -> T {
//     let size = MemoryLayout<T>.size
//     guard offset + size <= data.count else {
//       throw NSError(
//         domain: "BinaryDecoder", code: 1,
//         userInfo: [NSLocalizedDescriptionKey: "Unexpected end of data"])
//     }
//
//     let value = data.subdata(in: offset..<offset + size).withUnsafeBytes { bytes in
//       bytes.load(as: T.self).littleEndian
//     }
//     offset += size
//     return value
//   }
//
//   func decodeString() throws -> String {
//     let length = try decode(UInt32.self)
//     guard offset + Int(length) <= data.count else {
//       throw NSError(
//         domain: "BinaryDecoder", code: 1,
//         userInfo: [NSLocalizedDescriptionKey: "Unexpected end of data"])
//     }
//
//     let stringData = data.subdata(in: offset..<offset + Int(length))
//     offset += Int(length)
//
//     guard let string = String(data: stringData, encoding: .utf8) else {
//       throw NSError(
//         domain: "BinaryDecoder", code: 2,
//         userInfo: [NSLocalizedDescriptionKey: "Invalid UTF-8 string"])
//     }
//     return string
//   }
//
//   func decodeDate() throws -> Date {
//     let timestamp = try decode(Int64.self)
//     return Date(timeIntervalSince1970: Double(timestamp))
//   }
//
//   func decodeUUID() throws -> UUID {
//     guard offset + 16 <= data.count else {
//       throw NSError(
//         domain: "BinaryDecoder", code: 1,
//         userInfo: [NSLocalizedDescriptionKey: "Unexpected end of data"])
//     }
//
//     let uuidBytes = data.subdata(in: offset..<offset + 16)
//     offset += 16
//
//     let uuid = uuidBytes.withUnsafeBytes { rawBytes in
//       let bytes = rawBytes.bindMemory(to: UInt8.self)
//       let uuidBytes = (
//         bytes[0], bytes[1], bytes[2], bytes[3],
//         bytes[4], bytes[5], bytes[6], bytes[7],
//         bytes[8], bytes[9], bytes[10], bytes[11],
//         bytes[12], bytes[13], bytes[14], bytes[15]
//       )
//       return UUID(uuid: uuidBytes)
//     }
//     return uuid
//   }
//
//   func decodeEntry() throws -> LoginEntry {
//     let _ = try decodeUUID()
//     let title = try decodeString()
//     let username = try decodeString()
//     let password = try decodeString()
//     let notes = try decodeString()
//     let createdAt = try decodeDate()
//     let modifiedAt = try decodeDate()
//
//     return LoginEntry(
//       title: title,
//       username: username,
//       password: password,
//       notes: notes,
//       createdAt: createdAt,
//       modifiedAt: modifiedAt
//     )
//   }
//
//   func decodeEntries() throws -> [LoginEntry] {
//     let count = try decode(UInt32.self)
//     var entries: [LoginEntry] = []
//
//     for _ in 0..<count {
//       entries.append(try decodeEntry())
//     }
//
//     return entries
//   }
// }
