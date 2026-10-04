import XCTest
@testable import SourndAssets

final class SourndAssetsTests: XCTestCase {
    func testTokens() {
        let colour = SourndAssets.tokens["colour"] as? [String: Any]
        let petrol = colour?["petrol"] as? [String: Any]
        XCTAssertEqual(petrol?["light"] as? String, "#3A97A3")
    }

    func testMarksAndIcons() {
        XCTAssertNotNil(SourndAssets.mark(.light))
        XCTAssertNotNil(SourndAssets.mark(.dark))
        XCTAssertEqual(SourndAssets.iconCut(size: 16), .tiny)
        XCTAssertEqual(SourndAssets.iconCut(size: 32), .small)
        XCTAssertEqual(SourndAssets.iconCut(size: 48), .full)
        XCTAssertNotNil(SourndAssets.icon(size: 32))
        XCTAssertNotNil(SourndAssets.url("web/favicon.ico"))
    }

    func testFonts() {
        XCTAssertTrue(SourndAssets.registerFonts())
    }
}
