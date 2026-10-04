<?php

namespace Sournd\Assets;

/**
 * The sournd brand kit for PHP and Laravel: token values and the paths of the files.
 *
 * Assets::tokens()['colour']['petrol']['light'];   // '#3A97A3'
 * Assets::mark('dark');                            // .../marks/sournd-wordmark-dark.svg
 * Assets::icon(32);                                // the small cut
 * Assets::path('web/favicon.ico');
 */
final class Assets
{
    /** Brand kit version (semver). The major version is the brand generation. */
    public const VERSION = '0.1.0';

    /** @var array<string, mixed>|null */
    private static ?array $tokens = null;

    /** Absolute path of a file inside the package. */
    public static function path(string $relative = ''): string
    {
        return dirname(__DIR__).($relative === '' ? '' : '/'.ltrim($relative, '/'));
    }

    /** @return array<string, mixed> */
    public static function tokens(): array
    {
        return self::$tokens ??= json_decode(
            (string) file_get_contents(self::path('tokens/tokens.json')),
            true,
            flags: JSON_THROW_ON_ERROR,
        );
    }

    /** The wordmark SVG for a theme: light (on paper) or dark (on night). */
    public static function mark(string $theme = 'light'): string
    {
        return self::path("marks/sournd-wordmark-{$theme}.svg");
    }

    /** The icon cut for a pixel size: tiny below 20px, small up to 32px, full above. */
    public static function iconCut(int $px): string
    {
        return $px < 20 ? 'tiny' : ($px <= 32 ? 'small' : 'full');
    }

    /** The icon SVG for a cut name (full, small, tiny) or a pixel size. */
    public static function icon(int|string $sizeOrCut = 'full'): string
    {
        $cut = is_int($sizeOrCut) ? self::iconCut($sizeOrCut) : $sizeOrCut;

        return self::path("marks/sournd-icon-{$cut}.svg");
    }
}
