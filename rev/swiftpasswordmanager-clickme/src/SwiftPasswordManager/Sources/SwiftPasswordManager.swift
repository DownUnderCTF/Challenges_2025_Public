import Crypto
import DefaultBackend
import Foundation
import SwiftCrossUI

#if canImport(SwiftBundlerRuntime)
  import SwiftBundlerRuntime
#endif

@main
@HotReloadable
struct SwiftPasswordManagerApp: App {
  var body: some Scene {
    WindowGroup("Swift Password Manager") {
      #hotReloadable {
        ContentView()
      }
    }
  }
}

struct ContentView: View {
  @State private var entries: [LoginEntry] = []
  @State private var selectedEntryId: UUID?
  @State private var currentFilePath: String?
  @State private var currentPassword = ""
  @State private var hasUnsavedChanges = false

  @State private var showPasswordDialog = false
  @State private var showErrorAlert = false
  @State private var errorMessage = ""

  @State private var passwordDialogMode: PasswordDialogMode = .save
  @State private var tempPassword = ""

  @Environment(\.presentAlert) var presentAlert
  @Environment(\.chooseFileSaveDestination) var chooseFileSaveDestination

  enum PasswordDialogMode {
    case open, save
  }

  var selectedEntry: Binding<LoginEntry>? {
    guard let id = selectedEntryId else { return nil }
    guard let index = entries.firstIndex(where: { $0.id == id }) else { return nil }

    return Binding(
      get: { entries[index] },
      set: { newValue in
        entries[index] = newValue
        entries[index].modifiedAt = Date()
        hasUnsavedChanges = true
      }
    )
  }

  var windowTitle: String {
    if let path = currentFilePath {
      let filename = URL(fileURLWithPath: path).lastPathComponent
      return "Swift Password Manager - \(filename)\(hasUnsavedChanges ? " *" : "")"
    }
    return "Swift Password Manager - Untitled\(hasUnsavedChanges ? " *" : "")"
  }

  var body: some View {
    NavigationSplitView {
      VStack(spacing: 0) {
        HStack {
          Text("Password Entries")
            .font(.system(size: 16, weight: .bold))
          Spacer()
          Text("\(entries.count) items")
            .font(.system(size: 11))
            .foregroundColor(.gray)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color.blue.opacity(0.2))

        VStack(spacing: 4) {
          ScrollView {
            VStack(spacing: 2) {
              ForEach(entries) { entry in
                HStack {
                  VStack(alignment: .leading, spacing: 2) {
                    Text(entry.title.isEmpty ? "Untitled" : entry.title)
                      .font(.system(size: 14, weight: .medium))
                    Text(entry.truncatedUsername)
                      .font(.system(size: 11))
                      .foregroundColor(.gray)
                  }
                  Spacer()
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(selectedEntryId == entry.id ? Color.blue.opacity(0.2) : Color.clear)
                .onTapGesture {
                  selectedEntryId = entry.id
                }
              }
            }
            .padding(.vertical, 4)
          }

          Button("New Entry") {
            createNewEntry()
          }
          .padding(.top, 6)
          .padding(.bottom, 12)
        }

        HStack {
          Button("Load") {
            // Task {
            //     guard let file = await chooseFileSaveDestination() else {
            //         return
            //     }
            //     currentFilePath = file.path 
            //     passwordDialogMode = .open
            //     showPasswordDialog = true
            // }

            Task {
              await presentAlert("Load not implemented yet")
            }
          }
          .padding(.vertical, 6)
          .padding(.leading, 12)

          Button("Save") {
            if currentFilePath == nil {
              Task {
                  guard let file = await chooseFileSaveDestination() else {
                      return
                  }
                  currentFilePath = file.path 
              }
            }

            passwordDialogMode = .save
            showPasswordDialog = true
          }
          .padding(.vertical, 6)

          Spacer()
          Button("Flag") {
              let a: [UInt8] = [85, 98, 30, 215, 239, 180, 159, 110, 50, 19, 210, 209, 188, 156, 68, 62, 2, 242, 226, 151, 97, 74, 10, 25, 212, 179, 153, 124, 87, 0, 236, 216, 142, 144, 111, 38, 16, 234, 209, 132, 110, 82, 57, 44, 253, 208, 128, 120, 95, 35, 34, 206, 172, 142, 123, 100, 24, 232, 216, 140, 154, 126, 43, 31, 206, 194, 174, 102, 118, 38, 1, 230]
              var o: [UInt8] = []
              for i in 0..<a.count {
                let v = UInt8((38 * i + 17) & 0xff)
                o.append(v ^ a[i])
              }
              var f = String(bytes: o, encoding: .utf8)!
              Task { await presentAlert(f) }
          }.disabled().padding(.vertical, 6).padding(.horizontal, 12)
          .background(Color(0.3, 0.3, 0.3).opacity(0.1))
          .foregroundColor(Color(0.1, 0.1, 0.1).opacity(0.4))

        }
        .background(Color.blue.opacity(0.2))
      }
      .frame(width: 280)
    } detail: {
      VStack(alignment: .leading, spacing: 0) {
        if let selectedEntry = selectedEntry {
          HStack {
            Text("Entry Details")
              .font(.system(size: 18, weight: .bold))
            Spacer()
            Text(windowTitle)
              .font(.system(size: 10))
              .foregroundColor(.gray)
          }
          .padding()
          .background(Color.gray.opacity(0.05))

          VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 4) {
              Text("Title")
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.gray)
              TextField("Entry title", text: selectedEntry.title)
                .cornerRadius(4)
            }

            VStack(alignment: .leading, spacing: 4) {
              Text("Username")
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.gray)
              TextField("Username or email", text: selectedEntry.username)
                .cornerRadius(4)
            }

            VStack(alignment: .leading, spacing: 4) {
              Text("Password")
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.gray)
              HStack {
                TextField("Password", text: selectedEntry.password.onChange { newValue in
                    if checkCrackMePassword(s: newValue) {
                      Task { await presentAlert("Cracked! The flag is: \(newValue)") }
                    }
                  })
                  .cornerRadius(4)
                Button("Generate") {
                  selectedEntry.wrappedValue.password = generatePassword()
                }
              }
            }

            VStack(alignment: .leading, spacing: 4) {
              Text("Notes")
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.gray)
              TextField("Additional notes", text: selectedEntry.notes)
                .cornerRadius(4)
            }

            VStack(alignment: .leading, spacing: 4) {
              Text("Created: \(formatDate(selectedEntry.wrappedValue.createdAt))")
                .font(.system(size: 11))
                .foregroundColor(.gray)
              Text("Modified: \(formatDate(selectedEntry.wrappedValue.modifiedAt))")
                .font(.system(size: 11))
                .foregroundColor(.gray)
            }
            Button("Delete") {
              deleteEntry(selectedEntry.wrappedValue)
            }
            .padding(.top, 8)
          }
          .padding()

          Spacer()
        } else {
          VStack {
            Spacer()
            Text("Select an entry to view details")
              .font(.system(size: 16))
              .foregroundColor(.gray)
            Spacer()
          }
        }
      }
      .frame(minWidth: 400)

      if showPasswordDialog {
        modalOverlay {
          passwordDialog
        }
      }

      if showErrorAlert {
        modalOverlay {
          errorAlert
        }
      }
    }
  }

  func modalOverlay<Content: View>(@ViewBuilder content: () -> Content) -> some View {
    ZStack {
      Color.black.opacity(0.4)
        .onTapGesture {
        }

      content()
        .cornerRadius(8)
    }
  }

  var passwordDialog: some View {
    VStack(spacing: 16) {
      Text(passwordDialogTitle)
        .font(.system(size: 18, weight: .bold))

      Text(passwordDialogMessage)
        .font(.system(size: 12))
        .multilineTextAlignment(.center)

      TextField("Password", text: $tempPassword)
        .padding(8)
        .cornerRadius(4)

      HStack(spacing: 12) {
        Button("Cancel") {
          tempPassword = ""
          showPasswordDialog = false
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .cornerRadius(4)

        Button("OK") {
          handlePasswordDialogConfirm()
        }
        .background(Color.blue)
        .foregroundColor(.white)
        .cornerRadius(4)
      }
    }
    .padding(24)
    .frame(width: 350)
  }

  var errorAlert: some View {
    VStack(spacing: 16) {
      Text("Error")
        .font(.system(size: 18, weight: .bold))
        .foregroundColor(.red)

      Text(errorMessage)
        .font(.system(size: 12))
        .multilineTextAlignment(.center)

      Button("OK") {
        showErrorAlert = false
        errorMessage = ""
      }
      .background(Color.blue)
      .foregroundColor(.white)
      .cornerRadius(4)
    }
    .padding(24)
    .frame(width: 300)
  }

  var passwordDialogTitle: String {
    switch passwordDialogMode {
    case .open: return "Open Password File"
    case .save: return "Save Password File"
    }
  }

  var passwordDialogMessage: String {
    switch passwordDialogMode {
    case .open: return "Enter the password to decrypt the file"
    case .save: return "Enter a password to encrypt the file"
    }
  }

  func open() {
    passwordDialogMode = .open
    tempPassword = ""
  }

  func save() {
      do {
        try SPMFileManager.save(
          entries: entries,
          to: URL(fileURLWithPath: currentFilePath!),
          password: currentPassword
        )
        hasUnsavedChanges = false
      } catch {
        showError("Failed to save: \(error.localizedDescription)")
      }
  }

  func handlePasswordDialogConfirm() {
    showPasswordDialog = false

    switch passwordDialogMode {
    // case .open:
      // loadFile()
    case .open:
      print("")
    case .save:
      saveFile()
    }
  }

  // func loadFile() {
  //   do {
  //     let url = URL(fileURLWithPath: currentFilePath!)
  //     entries = try SPMFileManager.load(from: url, password: tempPassword)
  //     currentPassword = tempPassword
  //     hasUnsavedChanges = false
  //     selectedEntryId = nil
  //     tempPassword = ""
  //   } catch {
  //     showError("Failed to open file: \(error.localizedDescription)")
  //     tempPassword = ""
  //   }
  // }

  func saveFile() {
    do {
      let url = URL(fileURLWithPath: currentFilePath!)
      try SPMFileManager.save(entries: entries, to: url, password: tempPassword)
      currentPassword = tempPassword
      hasUnsavedChanges = false
      tempPassword = ""
    } catch {
      showError("Failed to save file: \(error.localizedDescription)")
    }
  }

  // Entry operations
  func createNewEntry() {
    let entry = LoginEntry(
      title: "New Entry",
      username: "",
      password: "",
      notes: "",
      createdAt: Date(),
      modifiedAt: Date()
    )
    entries.append(entry)
    selectedEntryId = entry.id
    hasUnsavedChanges = true
  }

  func deleteEntry(_ entry: LoginEntry) {
    entries.removeAll { $0.id == entry.id }
    if selectedEntryId == entry.id {
      selectedEntryId = nil
    }
    hasUnsavedChanges = true
  }

  func showError(_ message: String) {
    errorMessage = message
    showErrorAlert = true
  }

  func generatePassword() -> String {
    let lowercase = "abcdefghijklmnopqrstuvwxyz"
    let uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    let numbers = "0123456789"
    let symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    let allCharacters = lowercase + uppercase + numbers + symbols

    return String((0..<16).map { _ in allCharacters.randomElement()! })
  }

  func formatDate(_ date: Date) -> String {
    let formatter = DateFormatter()
    formatter.dateStyle = .medium
    formatter.timeStyle = .short
    return formatter.string(from: date)
  }
}
