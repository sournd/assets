//! sournd brand kit for Rust: the tokens, marks and fonts, embedded at compile time.
//!
//! ```
//! assert!(sournd_assets::TOKENS_JSON.contains("#3A97A3"));
//! assert_eq!(sournd_assets::icon_cut(32), "small");
//! let svg: &str = sournd_assets::wordmark_svg(sournd_assets::Theme::Dark);
//! assert!(svg.starts_with("<svg"));
//! ```

/// Brand kit version (semver). The major version is the brand generation.
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// `tokens/tokens.json`: colour, logo, icon, button states, type and interface sizes.
pub const TOKENS_JSON: &str = include_str!("../../tokens/tokens.json");
/// `tokens/tokens.css`: the same as CSS custom properties (`--sournd-*`).
pub const TOKENS_CSS: &str = include_str!("../../tokens/tokens.css");

pub const WORDMARK_LIGHT_SVG: &str = include_str!("../../marks/sournd-wordmark-light.svg");
pub const WORDMARK_DARK_SVG: &str = include_str!("../../marks/sournd-wordmark-dark.svg");
pub const ICON_FULL_SVG: &str = include_str!("../../marks/sournd-icon-full.svg");
pub const ICON_SMALL_SVG: &str = include_str!("../../marks/sournd-icon-small.svg");
pub const ICON_TINY_SVG: &str = include_str!("../../marks/sournd-icon-tiny.svg");

/// Bricolage Grotesque (wordmark, display, headings), variable TTF. SIL OFL 1.1.
pub const FONT_BRICOLAGE_GROTESQUE: &[u8] =
    include_bytes!("../../fonts/bricolage-grotesque/BricolageGrotesque[opsz,wdth,wght].ttf");
/// Instrument Sans (body, interface, labels, values), variable TTF. SIL OFL 1.1.
pub const FONT_INSTRUMENT_SANS: &[u8] =
    include_bytes!("../../fonts/instrument-sans/InstrumentSans[wdth,wght].ttf");

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Theme {
    /// On paper.
    Light,
    /// On night.
    Dark,
}

/// The wordmark SVG for a theme.
pub fn wordmark_svg(theme: Theme) -> &'static str {
    match theme {
        Theme::Light => WORDMARK_LIGHT_SVG,
        Theme::Dark => WORDMARK_DARK_SVG,
    }
}

/// The icon cut for a pixel size: tiny below 20px, small up to 32px, full above.
pub fn icon_cut(px: u32) -> &'static str {
    if px < 20 {
        "tiny"
    } else if px <= 32 {
        "small"
    } else {
        "full"
    }
}

/// The icon SVG for a pixel size.
pub fn icon_svg(px: u32) -> &'static str {
    match icon_cut(px) {
        "tiny" => ICON_TINY_SVG,
        "small" => ICON_SMALL_SVG,
        _ => ICON_FULL_SVG,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn embedded_assets() {
        assert!(TOKENS_JSON.contains("\"petrol\""));
        assert!(TOKENS_CSS.contains("--sournd-petrol"));
        assert_eq!(icon_cut(16), "tiny");
        assert_eq!(icon_cut(24), "small");
        assert_eq!(icon_cut(48), "full");
        assert!(icon_svg(1024).starts_with("<svg"));
        assert_eq!(&FONT_BRICOLAGE_GROTESQUE[..4], &[0, 1, 0, 0]);
        assert_eq!(&FONT_INSTRUMENT_SANS[..4], &[0, 1, 0, 0]);
    }
}
