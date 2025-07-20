import Foundation

class SPMFileManager {
  static func save(entries: [LoginEntry], to url: URL, password: String) throws {
    let encoder = BinaryEncoder()
    encoder.encode(entries)
    let entriesData = encoder.finalize()

    let salt = CryptoHelper.generateSalt()

    guard let key = CryptoHelper.deriveKey(from: password, salt: salt),
      let encrypted = CryptoHelper.encrypt(data: entriesData, key: key)
    else {
      throw NSError(
        domain: "SPM", code: 1, userInfo: [NSLocalizedDescriptionKey: "Encryption failed"])
    }

    var fileData = Data()

    // Magic number
    fileData.append(contentsOf: withUnsafeBytes(of: SPMFileHeader.magic.littleEndian) { Data($0) })

    // Version
    fileData.append(contentsOf: withUnsafeBytes(of: UInt16(1).littleEndian) { Data($0) })

    // Flags (reserved)
    fileData.append(contentsOf: withUnsafeBytes(of: UInt16(0).littleEndian) { Data($0) })

    // Salt size and data
    fileData.append(contentsOf: withUnsafeBytes(of: UInt16(salt.count).littleEndian) { Data($0) })
    fileData.append(salt)

    // Nonce size and data
    fileData.append(
      contentsOf: withUnsafeBytes(of: UInt16(encrypted.nonce.count).littleEndian) { Data($0) })
    fileData.append(encrypted.nonce)

    // Tag size and data
    fileData.append(
      contentsOf: withUnsafeBytes(of: UInt16(encrypted.tag.count).littleEndian) { Data($0) })
    fileData.append(encrypted.tag)

    // Encrypted data size and data
    fileData.append(
      contentsOf: withUnsafeBytes(of: UInt32(encrypted.ciphertext.count).littleEndian) { Data($0) })
    fileData.append(encrypted.ciphertext)

    try fileData.write(to: url)
  }

  // static func load(from url: URL, password: String) throws -> [LoginEntry] {
  //   let fileData = try Data(contentsOf: url)
  //   var offset = 0
  //
  //   // Read and verify magic number
  //   guard fileData.count >= 4 else {
  //     throw NSError(
  //       domain: "SPM", code: 3, userInfo: [NSLocalizedDescriptionKey: "Invalid file format"])
  //   }
  //
  //   let magic = fileData.subdata(in: 0..<4).withUnsafeBytes {
  //     $0.load(as: UInt32.self).littleEndian
  //   }
  //   guard magic == SPMFileHeader.magic else {
  //     throw NSError(
  //       domain: "SPM", code: 3, userInfo: [NSLocalizedDescriptionKey: "Invalid file format"])
  //   }
  //   offset += 4
  //
  //   // Read version
  //   let version = fileData.subdata(in: offset..<offset + 2).withUnsafeBytes {
  //     $0.load(as: UInt16.self).littleEndian
  //   }
  //   guard version == 1 else {
  //     throw NSError(
  //       domain: "SPM", code: 4, userInfo: [NSLocalizedDescriptionKey: "Unsupported file version"])
  //   }
  //   offset += 2
  //
  //   // Skip flags
  //   offset += 2
  //
  //   // Read salt
  //   let saltSize = fileData.subdata(in: offset..<offset + 2).withUnsafeBytes {
  //     $0.load(as: UInt16.self).littleEndian
  //   }
  //   offset += 2
  //   let salt = fileData.subdata(in: offset..<offset + Int(saltSize))
  //   offset += Int(saltSize)
  //
  //   // Read nonce
  //   let nonceSize = fileData.subdata(in: offset..<offset + 2).withUnsafeBytes {
  //     $0.load(as: UInt16.self).littleEndian
  //   }
  //   offset += 2
  //   let nonce = fileData.subdata(in: offset..<offset + Int(nonceSize))
  //   offset += Int(nonceSize)
  //
  //   // Read tag
  //   let tagSize = fileData.subdata(in: offset..<offset + 2).withUnsafeBytes {
  //     $0.load(as: UInt16.self).littleEndian
  //   }
  //   offset += 2
  //   let tag = fileData.subdata(in: offset..<offset + Int(tagSize))
  //   offset += Int(tagSize)
  //
  //   // Read encrypted data
  //   let dataSize = fileData.subdata(in: offset..<offset + 4).withUnsafeBytes {
  //     $0.load(as: UInt32.self).littleEndian
  //   }
  //   offset += 4
  //   let encryptedData = fileData.subdata(in: offset..<offset + Int(dataSize))
  //
  //   // Decrypt
  //   guard let key = CryptoHelper.deriveKey(from: password, salt: salt),
  //     let decryptedData = CryptoHelper.decrypt(
  //       ciphertext: encryptedData,
  //       key: key,
  //       nonce: nonce,
  //       tag: tag
  //     )
  //   else {
  //     throw NSError(
  //       domain: "SPM", code: 2,
  //       userInfo: [NSLocalizedDescriptionKey: "Decryption failed - wrong password?"])
  //   }
  //
  //   let decoder = BinaryDecoder(data: decryptedData)
  //   return try decoder.decodeEntries()
  // }
}

