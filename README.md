<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="design/brand/github/readme-banner-dark.png">
    <img alt="UnboundFS — Storage without boundaries." src="design/brand/github/readme-banner-light.png" width="840">
  </picture>
</p>

<p align="center"><b>A free and open-source macOS utility for using Windows and Linux drives on a Mac.</b></p>

> [!IMPORTANT]
> **UnboundFS is in early planning. There is no working software yet.** No releases exist, and nothing in
> this repository mounts, reads or writes drives today. Everything listed under "Goals" is planned, not
> implemented. Do not use any future pre-release build on drives holding data you have not backed up.

## Vision

Plugging a Windows-formatted drive into a Mac should just work. UnboundFS aims to become a polished,
native macOS app that lets you use external SSDs, hard drives and USB sticks formatted for Windows
(NTFS first) and, later, Linux, without buying a commercial driver.

## Goals (planned, not implemented)

- NTFS read and write access to external drives, with Finder integration
- Automatic read-only mode when writing would be unsafe (Windows Fast Startup, hibernation, a dirty volume)
- Drive detection, mounting, unmounting and safe eject from a native menu bar app
- Drive information and storage usage
- Updates delivered through GitHub releases
- Later: ext2/3/4 and other Linux filesystems where it is technically feasible

Which of these are achievable, and on which macOS versions, is being assessed in the Phase 1 technical
feasibility review.

## Commitments

UnboundFS is and will remain **free and open-source software**:

- No paid or premium editions, subscriptions, trials or advertisements
- No accounts and no telemetry; works offline
- Native macOS app (Swift), not a web wrapper
- Data integrity before features: when in doubt, mount read-only

## Intended platforms

Apple Silicon and, where feasible, Intel Macs, on macOS 15 Sequoia and macOS 26 Tahoe or later.
Exact support depends on the outcome of the feasibility review.

## Project status

| Phase | Status |
|---|---|
| 0 — Visual identity | Done. Owner selected **Shear (Silver & Ember)**. See [`design/brand/`](design/brand/). |
| 1 — Technical feasibility | In review: filesystem backends, signing, distribution and data-safety research |
| 2 — Application and filesystem engine | Not started; begins only after the owner approves the Phase 1 architecture |

## Brand

<img src="design/brand/app-icon/png/AppIcon-default-1024.png" width="96" align="left" alt="UnboundFS app icon">

The identity is a storage disc split along a fault line, with the boundary itself exposed in Ember.
Assets, colours and usage rules are in [`design/brand/`](design/brand/) and the
[brand guidelines](design/brand/GUIDELINES.md). Earlier concepts are preserved in
[`design/archive/`](design/archive/).
<br clear="left">

## License

UnboundFS is licensed under the [GNU General Public License v2.0](LICENSE). Whether the project will use
"GPL-2.0-only" or "GPL-2.0-or-later" will be confirmed once its dependencies are chosen.

Windows is a trademark of Microsoft Corporation; macOS and Finder are trademarks of Apple Inc. UnboundFS is an independent project and is not affiliated
with Microsoft, Apple, Tuxera or Paragon Software.
