import CoreText
import Foundation

/// The sournd brand kit: token values, mark files and the brand fonts.
///
///     let petrol = SourndAssets.tokens["colour"]...      // decoded tokens.json
///     SourndAssets.mark(.dark)                           // URL of the dark wordmark SVG
///     SourndAssets.icon(size: 32)                        // the small cut
///     SourndAssets.registerFonts()                       // Bricolage Grotesque + Instrument Sans
public enum SourndAssets {
    /// Brand kit version (semver). The major version is the brand generation.
    public static let version = "0.1.0"

    public enum Theme: String { case light, dark }
    public enum IconCut: String { case full, small, tiny }

    /// URL of a resource copied into the package, e.g. "tokens/tokens.json" or "web".
    public static func url(_ relative: String) -> URL? {
        let parts = relative.split(separator: "/").map(String.init)
        guard let first = parts.first, var url = Bundle.module.url(forResource: first, withExtension: nil) else {
            return nil
        }
        for part in parts.dropFirst() { url.appendPathComponent(part) }
        return FileManager.default.fileExists(atPath: url.path) ? url : nil
    }

    /// tokens.json, decoded.
    public static let tokens: [String: Any] = {
        guard let url = url("tokens/tokens.json"), let data = try? Data(contentsOf: url),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return [:] }
        return json
    }()

    /// The wordmark SVG: light (on paper) or dark (on night).
    public static func mark(_ theme: Theme = .light) -> URL? {
        url("sournd-wordmark-\(theme.rawValue).svg")
    }

    /// The icon cut for a pixel size: tiny below 20pt, small up to 32pt, full above.
    public static func iconCut(size: Int) -> IconCut {
        size < 20 ? .tiny : (size <= 32 ? .small : .full)
    }

    public static func icon(_ cut: IconCut = .full) -> URL? {
        url("sournd-icon-\(cut.rawValue).svg")
    }

    public static func icon(size: Int) -> URL? {
        icon(iconCut(size: size))
    }

    /// Registers Bricolage Grotesque and Instrument Sans with the process (call once at launch).
    @discardableResult
    public static func registerFonts() -> Bool {
        let files = [
            "fonts/bricolage-grotesque/BricolageGrotesque[opsz,wdth,wght].ttf",
            "fonts/instrument-sans/InstrumentSans[wdth,wght].ttf",
            "fonts/instrument-sans/InstrumentSans-Italic[wdth,wght].ttf",
        ]
        var ok = true
        for file in files {
            let name = String(file.split(separator: "/").last ?? "")
            let folder = file.hasPrefix("fonts/bricolage") ? "bricolage-grotesque" : "instrument-sans"
            guard let url = url(folder + "/" + name) else { ok = false; continue }
            ok = CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil) && ok
        }
        return ok
    }
}
