# UnboundFS — Phase 1 technical feasibility report

**Scope:** free NTFS read/write access to external drives on macOS with Finder integration.
**Status:** research only, for owner review. No application code was written, no driver was installed,
and no test was run on any physical drive.
**Date:** 24 November 2026.

## How to read this report

Every finding is labelled:

| Label | Meaning |
|---|---|
| **✅ Verified** | Stated in a primary source: Apple documentation or an Apple engineer, upstream source or license text |
| **🟡 Reported** | Stated in a third-party project's documentation; plausible but not reproduced by us |
| **❓ Unverified** | Not established; an assumption, conflicting sources, or needs hardware testing |

Nothing in this report was tested on a Mac. Findings marked 🟡 or ❓ must be confirmed in the staged
tests described in section 9 before anything is promised to users.

---

## 1. Summary

1. **Kext-free NTFS read/write with Finder integration is technically possible** with an Apple **FSKit**
   file-system extension that wraps **libntfs-3g**. Several GPL projects already do this (xntfs, ntfs4mac,
   MNtfs and others). 🟡
2. **FSKit needs a paid Apple Developer Program team.** Extensions must carry
   `com.apple.developer.fskit.fsmodule`, a *restricted* entitlement that must be authorised by a provisioning
   profile, and Apple DTS states that creating that profile requires a paid team. Ad-hoc signing does not
   work. ✅ ([Apple DTS](https://developer.apple.com/forums/thread/817501))
3. **The cost falls on the project, not on users.** A Developer ID-signed, notarized DMG runs on any Mac
   without the user holding any account (MNtfs reports exactly this 🟡). End users still have to switch the
   extension on once in System Settings. ✅
4. **The critical requirements cannot all be met at once.** "No paid Apple Developer membership" conflicts
   with "native Finder read/write without kext, SIP changes or Reduced Security". Every path that avoids
   the paid membership breaks another requirement (section 3).
5. **macOS 15 Sequoia is uncertain for read/write.** FSKit exists from 15.4, but projects disagree on whether
   a third-party NTFS module can take a physical NTFS volume away from Apple's built-in read-only NTFS
   support on 15.x. ntfs4mac reports it cannot on 15.7.9 and recommends macOS 26; MNtfs claims 15.4+;
   xntfs offers a per-volume Terminal workaround. ❓ This must be tested on the owner's 15.6.1 Mac with disk
   images before any Sequoia promise is made.
6. **macOS 26 Tahoe is the realistic read/write target.** All FSKit NTFS projects report automount and
   read/write there. 🟡

**Recommendation:** Swift menu bar app + FSKit extension + libntfs-3g, distributed as a Developer
ID-signed, notarized DMG, with read-only as the default and writes allowed only after safety checks.
This needs an Apple Developer Program membership held by the owner or a sponsoring organisation.
Without it, the code can still be built and tested in CI, but nobody can run the FSKit extension.

---

## 2. Answers to the nine questions

| # | Question | Answer |
|---|---|---|
| 1 | Can physical NTFS volumes be mounted read/write on macOS 15.6.1? | **Unknown, possibly not.** FSKit and Disk Arbitration automount are present (automount broken only on 15.4/15.5 🟡). One project reports third-party FSKit NTFS volumes cannot be mounted on 15.7.9 because Apple's read-only driver takes priority 🟡; another claims 15.4+ works 🟡. ❓ Needs testing. |
| 2 | Does the same implementation work on macOS 26? | **Yes, as reported.** All FSKit NTFS projects target and test macOS 26 🟡. macOS 26 also adds `FSPathURLResource` and `FSGenericURLResource` 🟡. One FSKit binary can support both versions, with version-specific behaviour. |
| 3 | Signing, entitlement, provisioning and distribution requirements | FSKit: restricted entitlement + provisioning profile from a paid team; Developer ID signing + notarization for distribution outside the App Store ✅. macFUSE apps: no special entitlement for the app itself; users install macFUSE separately ✅. Unsigned or ad-hoc apps: Gatekeeper on Sequoia needs System Settings → Privacy & Security → Open Anyway ✅. Details in section 5. |
| 4 | Is a free Apple account or ad-hoc signing enough? | **No, for FSKit.** Ad-hoc signing cannot authorise restricted entitlements, and DTS says the profile needs a paid team ✅. MNtfs reports "free personal teams are refused" 🟡. Ad-hoc is enough only for non-FSKit pieces (menu bar app, read-only tools, macFUSE-based file systems). |
| 5 | Can GitHub Actions build and meaningfully test each backend? | **Build: yes. Engine tests on disk images: yes. Live FSKit mounts: no.** macOS 26 (arm64 and Intel) and macOS 15 runners exist ✅. FSKit extensions need a user toggle in System Settings and a valid profile, which hosted runners cannot provide ❓. Section 11 has the full table. |
| 6 | Security changes, admin rights, external drivers or private APIs? | FSKit path: no SIP or Reduced Security change, no kext, no private API; one System Settings toggle; admin only for an optional `/Library/Filesystems` naming bundle 🟡. macFUSE kernel backend: Reduced Security on Apple Silicon ✅. microVM: `sudo` for raw disk access 🟡. |
| 7 | Is standalone Finder integration genuinely possible? | **Yes with FSKit** (volumes appear under `/Volumes`, in Finder and Disk Utility 🟡). With macFUSE, a separate macFUSE install is needed. With the microVM approach, Finder sees an NFS network volume. |
| 8 | Can dependencies be legally redistributed in a free GPL app? | **libntfs-3g: yes** (GPL) ✅. **Sparkle: yes** (MIT). **macFUSE:** its license forbids bundling with *commercial* software without permission ✅; UnboundFS is non-commercial, but written permission is advisable before bundling the installer. Section 6. |
| 9 | Expected performance and reliability limits | ntfs-3g is mature but effectively single-threaded per volume 🟡; FSKit adds per-operation overhead and is a young API with known bugs 🟡. Expect well below kernel-driver speed for metadata-heavy work; large sequential copies should be USB-bound. Section 8. |

---

## 3. Requirement scorecard

Approaches compared:

- **A.** FSKit extension + libntfs-3g, Developer ID-notarized DMG (**recommended**)
- **B.** UnboundFS app + ntfs-3g on **macFUSE's FSKit backend** (user installs macFUSE)
- **C.** ntfs-3g on **macFUSE's kernel backend** (classic setup)
- **D.** **microVM**: Linux `ntfs3` driver in a lightweight VM, exported over NFS (anylinuxfs-style)
- **E.** **Read-only companion**: Apple's built-in read-only NTFS + UnboundFS drive manager, no write support

| Requirement | A | B | C | D | E |
|---|---|---|---|---|---|
| Free and open-source | ✅ | ⚠️ macFUSE partly closed | ⚠️ closed kext | ✅ (to verify per component) | ✅ |
| No paid runtime components | ✅ | ✅ | ✅ | ✅ | ✅ |
| No subscriptions, ads, accounts, telemetry | ✅ | ✅ | ✅ | ✅ | ✅ |
| No mandatory Homebrew | ✅ | ✅ (macFUSE has a .pkg) | ✅ | ⚠️ today via Homebrew; could be bundled | ✅ |
| Standalone DMG | ✅ | ❌ separate macFUSE install | ❌ | ✅ | ✅ |
| No kernel extension | ✅ | ✅ | ❌ | ✅ | ✅ |
| No disabling SIP | ✅ | ✅ | ✅ | ✅ | ✅ |
| No Reduced Security | ✅ | ✅ | ❌ on Apple Silicon | ✅ | ✅ |
| **No paid Apple Developer membership** | ❌ | ✅* | ✅* | ❓* | ✅* |
| Native Finder read/write | ✅ | ✅ (via macFUSE) | ✅ | ⚠️ NFS network volume | ❌ read-only |
| Physical SSD/HDD/USB drives | ✅ on 26 🟡, ❓ on 15 | ❓ device access undocumented | ✅ | ✅ 🟡 | ✅ |
| Offline | ✅ | ✅ | ✅ | ✅ | ✅ |
| Low CPU and memory | ✅ | ⚠️ | ✅ | ❌ VM memory | ✅ |
| Strong data integrity | ✅ ntfs-3g | ✅ ntfs-3g | ✅ ntfs-3g | ⚠️ ntfs-3g misbehaves over NFS 🟡; kernel `ntfs3` | ✅ no writes |

\* Without notarization, users must approve the app once in System Settings → Privacy & Security (Sequoia
removed the Control-click bypass ✅).

**No approach meets every requirement.** A misses only the paid membership requirement. E meets every
requirement except writing.

---

## 4. Backend findings

### 4.1 Apple FSKit

- Introduced in **macOS 15.4**; early releases support only `FSUnaryFileSystem` (one resource, one
  volume), meant for "traditional file systems ... FAT, HFS, and so on". The module's entry point must be
  Swift. ✅ [DTS](https://developer.apple.com/forums/thread/776322)
- Needs the restricted `com.apple.developer.fskit.fsmodule` entitlement and a paid team's provisioning
  profile. ✅ [DTS](https://developer.apple.com/forums/thread/817501)
- The user enables the module in **System Settings → General → Login Items & Extensions → File System
  Extensions**. ✅ [Apple engineer](https://developer.apple.com/forums/thread/776322) Enablement is per user,
  so `sudo mount` does not work 🟡 ([ext4mac](https://github.com/xVanTuring/ext4all/blob/main/ext4mac/README.md)).
  Re-signing or reinstalling resets the enabled state 🟡 ([GHFS](https://github.com/indragiek/GHFS/blob/main/FSKIT.md)).
- Physical disks come in as `FSBlockDeviceResource` (`bsdName`, `blockSize`, direct read/write). 🟡 Manual
  mounting uses `mount -F -t <type> diskNsM <dir>`. ✅ (DTS)
- Disk Arbitration fails to probe FSKit modules on **15.4/15.5** (Apple bug FB17772372), so automount works
  from 15.6. 🟡 ([ntfs4mac](https://github.com/vahidzekic/ntfs4mac))
- macOS 26 adds `FSPathURLResource` and `FSGenericURLResource`. 🟡 (GHFS)
- Known issues and limits 🟡:
  - FSKit offers no way to make the disk flush its own write cache.
  - The kernel side hands the extension up to 8 concurrent writes.
  - Kernel-offloaded I/O has undocumented caching behaviour, and one project found and fixed a data-loss
    bug in it.
  - `fskitd` caches failed probes.
  - Sources: [ext4mac](https://github.com/xVanTuring/ext4all/blob/main/ext4mac/README.md), [GHFS](https://github.com/indragiek/GHFS/blob/main/FSKIT.md).
- The extension runs sandboxed, cannot join App Groups, and the system hands it only the resource it
  mounts. 🟡

### 4.2 NTFS-3G / libntfs-3g

- Upstream: [tuxera/ntfs-3g](https://github.com/tuxera/ntfs-3g). The drivers, ntfsprogs and libntfs-3g are
  all GPL; Debian packages them as GPL-2+. ✅ The exact per-file wording in the 2022.10.3 tree should be
  re-read before release. ❓
- It is the engine behind every FSKit NTFS project found, built **without FUSE** and linked into the
  extension. 🟡
- It is mature (around 15 years in Linux distributions) and handles large files, sparse files and
  Unicode names. Write support for compressed and encrypted (EFS) data is limited or rejected by FSKit
  projects. 🟡
- Not designed for concurrent calls: FSKit projects serialise all I/O per volume. 🟡
- Upstream release cadence is slow; 2022.10.3 is the version these projects use. Whether newer upstream
  releases exist was not established. ❓ Security fixes for crafted images were part of the 2021 and
  2022 releases. 🟡 Fuzzing is part of the test plan (section 9).

### 4.3 macFUSE (including the FSKit backend)

- **Kernel backend:** the default. On Apple Silicon it needs **Reduced Security** with user-managed kernel
  extensions, set in Recovery. It cannot load when macOS boots from an external volume or in VMs. ✅
  ([Getting Started](https://github.com/macfuse/macfuse/wiki/Getting-Started))
- **FSKit backend:** opt-in with `-o backend=fskit`, built on FSKit (macOS 15.4+). It needs no kext and no
  Recovery changes. Documented limits: no notification API, most kernel mount options missing, and I/O
  "not on par" with the kernel backend. ✅ ([FUSE Backends](https://github.com/macfuse/macfuse/wiki/FUSE-Backends))
- Release notes (from search summaries; the pages themselves could not be fetched from this environment):
  - 5.1 added the FSKit backend.
  - 5.3 sped up FSKit reads by up to 15×.
  - 5.5 added read-only FSKit mounts on macOS 26.4+ and worked around an FSKit data-corruption issue on
    macOS 26/27.
  - Status 🟡; [5.5.0 notes](https://macfuse.github.io/2026/10/17/macfuse-5.5.0.html).
- **Not documented:** whether the FSKit backend can give a FUSE file system such as ntfs-3g access to a
  physical block device, and whether a third-party FUSE app needs its own entitlement. ❓
- **License:** BSD-style, with clause 4: *"Redistributions in binary form, bundled with commercial
  software, are not allowed without specific prior written permission."* The kernel extension has been
  closed source since 3.9 (2019); the last fully open release is 3.8.3. ✅
  ([LICENSE](https://github.com/macfuse/macfuse/blob/master/LICENSE.txt), [Open Source Status](https://github.com/macfuse/macfuse/wiki/Open-Source-Status))
- macFUSE itself does not provide NTFS; ntfs-3g on macOS has relied on macFUSE. ✅ ([FAQ](https://github.com/macfuse/macfuse/wiki/Frequently-Asked-Questions))

### 4.4 "OpenMacFUSE"

- No project of that name was found. ❓
- The closest matches:
  - **osxfuse 3.8.3**, the last fully open macFUSE (2018, kext-based, unsuitable for current macOS). ✅
  - **[fusetta](https://github.com/hsorbo/fusetta)**, described as "Open Source FUSE using FSKit". Its
    maturity was not evaluated. ❓
- If the owner meant a specific project, a link is needed.

### 4.5 NTFS4Mac and other open-source FSKit NTFS projects

| Project | Engine | License | Distribution | Notes |
|---|---|---|---|---|
| [ntfs4mac](https://github.com/vahidzekic/ntfs4mac) | FSKit + libntfs-3g 2022.10.3 | GPL-2.0-or-later | Build yourself; paid team required | Work in progress. Read-only on macOS 15 in practice ("use macOS 26 or later for read-write"). Hibernated volumes fall back to read-only. No xattrs or ADS. Tested on RAM disks and images on one Intel Mac only. 🟡 |
| [xntfs](https://github.com/HuanchuanTech/xntfs) | FSKit + ntfs-3g | GPLv2 | Mac App Store | Claims physical drives. On macOS 15 "the built-in NTFS driver may take priority" (provides a Terminal command). Stores xattrs as ADS. Rejects compressed-stream writes. 🟡 |
| [MNtfs](https://github.com/maclifevn/mntfs) | FSKit + libntfs-3g | GPL-2.0 | Developer ID, notarized DMG, Sparkle | Claims 15.4+, Apple Silicon. Strongest safety policy: never resets `$LogFile` or deletes `hiberfil.sys`; read-only when state is unsafe; write-error barrier. Version 0.1. 🟡 |
| [ntfstool](https://github.com/ntfstool/ntfstool), [branchway-ntfs](https://github.com/prashantguleria/branchway-ntfs), [xmac-ntfs](https://github.com/trinhhaox/xmac-ntfs) | FSKit + libntfs-3g | GPL | Various | Not evaluated in depth. |

**Observation:** in 2026 several near-identical GPL FSKit NTFS projects appeared, all young (dozens of
commits, single maintainers, little CI). UnboundFS should decide whether to build its own extension or
contribute to and build on one of them; their code is GPL-compatible with this project. ❓

### 4.6 Other approaches

- **[FUSE-T](https://github.com/macos-fuse-t/fuse-t):** kext-free FUSE through a local NFS, SMB or FSKit
  server. Its license is listed as "other", and it was not verified to be open source or to work with
  ntfs-3g on raw devices. ❓
- **microVM ([anylinuxfs](https://github.com/nohajc/anylinuxfs)):**
  - Runs Linux under libkrun, mounts the drive with Linux drivers and exports it to macOS over
    localhost NFS. No kext and no security changes. 🟡
  - Needs `sudo` for the raw device and is installed through Homebrew today. 🟡
  - ntfs-3g misbehaves over NFS, while the kernel `ntfs3` driver does not. 🟡
  - Heavy for NTFS, but it is the most realistic route to **btrfs and XFS** later.
- **New NTFS engine from scratch:** rejected. Rewriting a journaling filesystem's write path is the
  highest-risk option for data integrity.

---

## 5. Signing, entitlements and distribution

| Item | FSKit (A) | macFUSE (B, C) | Read-only companion (E) |
|---|---|---|---|
| Extension entitlement | `com.apple.developer.fskit.fsmodule` (restricted) ✅ | none for the app ❓ | none |
| Provisioning profile | Required; paid team ✅ | Not required | Not required |
| Developer ID signing + notarization | Required for frictionless install (paid) | Recommended (paid) | Recommended (paid) |
| Without paid membership | Cannot run at all ✅ | Runs after Open Anyway ✅ | Runs after Open Anyway ✅ |
| User steps | Enable extension in System Settings | Install macFUSE (+ Recovery steps for kernel backend) | None beyond first launch |
| Admin password | Optional, for the Disk Utility name bundle 🟡 | macFUSE installer | No |

- **Gatekeeper on Sequoia:** Control-click no longer bypasses Gatekeeper; users approve unnotarized apps
  in System Settings → Privacy & Security. ✅ ([Apple](https://developer.apple.com/news/?id=saqachfa))
- **Mac App Store:** possible for FSKit (xntfs ships there 🟡), but it also needs the paid membership, and
  GPL code on the App Store carries a known terms-compatibility risk. Prefer the DMG.
- **Sparkle updates:** EdDSA update signing is free. A smooth update experience still assumes notarized
  builds. ❓

---

## 6. Dependencies and licensing

| Component | License | Compatible with UnboundFS (GPL-2.0)? |
|---|---|---|
| libntfs-3g (ntfs-3g) | GPL (Debian: GPL-2+) ✅ | Yes |
| Sparkle 2 | MIT | Yes |
| Apple system frameworks (FSKit, DiskArbitration, SwiftUI) | System libraries | Yes (GPL system-library exception) |
| macFUSE installer (fallback only) | BSD-style + clause 4, closed kext | Not linked; separate install. Ask the author before bundling |
| ext4mac `ext4-core` (future) | GPL-3.0-or-later 🟡 | **Only if UnboundFS is GPL-2.0-or-later** |
| Linux kernel / `ntfs3` in a VM (future) | GPL-2.0 | Separate program in the VM image |

**GPL-2.0-only vs GPL-2.0-or-later:** libntfs-3g is GPL-2+, so both choices work today. GPL-2.0-only would
block future GPL-3.0 components (for example ext4mac's engine). **Recommendation: GPL-2.0-or-later.**
Declare it in SPDX headers and the README; the existing `LICENSE` text stays. This is the owner's decision.

---

## 7. Security implications

- **FSKit:** file-system parsing runs in a sandboxed user-space extension that receives only the device
  it mounts. 🟡 A bug in libntfs-3g triggered by a malicious drive is contained, unlike a kernel driver.
  Crafted-image bugs in ntfs-3g have existed in the past 🟡, so fuzzing is mandatory.
- **No root helper** is needed on the FSKit path; `fskitd` opens the device. 🟡
- **macFUSE kernel backend:** loading a third-party kext and lowering boot security weakens the whole
  system. ✅ Not acceptable as a default.
- **microVM:** runs a full Linux kernel; good isolation, but needs root for raw device access. 🟡
- **Supply chain:** vendor ntfs-3g by exact release tarball and checksum, build from source in CI, publish
  an SBOM. Use no network access at runtime other than optional update checks.

---

## 8. Performance and reliability

- FSKit adds an XPC/kernel round trip per operation, and macFUSE documents FSKit I/O as slower than its
  kext. ✅
- Reported throughput for an FSKit ext4 module on a 10 Gbps USB NVMe:
  - about 424 MB/s for uncached 1 MB writes
  - up to about 997 MB/s with parallel reads and writes 🟡
- NTFS through libntfs-3g will be slower because I/O is serialised.
- **Expectation:** large file copies limited by the USB link; slower creation of many small files and
  slower directory operations than commercial kernel drivers. ❓ To be measured in Phase 2.
- **Reliability risks:**
  - FSKit is young: it arrived in 15.4, Disk Arbitration was broken until 15.6 🟡, and there are reports
    of an FSKit data-corruption issue on macOS 26/27 🟡.
  - FSKit cannot force a drive to flush its write cache 🟡.
  - The engine itself (ntfs-3g) is mature.
- Memory and CPU at idle should be negligible for the FSKit path, since the extension runs only while a
  volume is mounted. ❓

---

## 9. Data integrity and testing strategy

### 9.1 Safety policy: read-only unless provably safe

Before any read/write mount, the extension inspects the volume read-only and **mounts read-only** if any
of these hold:

| Condition | Detection |
|---|---|
| Windows hibernated, or **Fast Startup** active | `hiberfil.sys` present with an active hibernation signature (libntfs-3g has a hiberfile check) |
| Volume marked **dirty** | `$Volume` flags |
| Journal (`$LogFile`) not clean | libntfs-3g logfile check. **Never reset `$LogFile` automatically** (MNtfs policy 🟡; ntfs-3g's recovery options can discard Windows' pending changes) |
| BitLocker | Volume signature: refuse to mount, explain why |
| Unsupported features in use | Compressed or EFS write targets rejected per file; deduplication reparse points read-only |
| Device reports write-protect, or I/O errors | Medium attributes; error barrier |

The app explains every read-only decision in plain language ("Windows did not shut down completely: turn
off Fast Startup or run chkdsk on Windows"), with no option to force writes in the first releases.

### 9.2 Operational safeguards

- **Safe eject:** flush, then `DADiskUnmount` and `DADiskEject`. Refuse while files are open and list the
  apps holding them.
- **Unexpected disconnection:**
  - Stop all writes at the first device error and keep the error until eject (write barrier).
  - On the next mount the volume is dirty, so it mounts read-only until chkdsk has run.
- **Files larger than 4 GB:** native to NTFS. Test 5 GB and 50 GB files, sparse files, and appends across
  4 GB boundaries.
- **Unicode:**
  - NTFS stores UTF-16 names, case-insensitively, using `$UpCase`.
  - Normalise names to NFC on disk so Windows sees the same names (ntfs-3g has a macOS NFC conversion
    option 🟡).
  - Reject Windows-invalid names (`<>:"\|?*`, `CON`, `NUL` and others) with a clear error.
  - Test case-only renames.
- **Permissions and attributes:**
  - No Windows ACL mapping at first. Files appear owned by the logged-in user.
  - Map the read-only and hidden attributes.
  - Store macOS extended attributes and Finder tags in NTFS alternate data streams rather than `._`
    files. Decide this before 1.0, because the on-disk format is hard to change later.
- **Large drives:** GPT disks above 2 TB, 4Kn drives, cluster sizes from 4 KB up to the largest Windows
  supports. Large clusters need verification against libntfs-3g. ❓
- **Concurrency:** one serial I/O queue per volume, because FSKit delivers up to 8 concurrent writes and
  libntfs-3g is not re-entrant 🟡.

### 9.3 Staged validation (no experimental writes on real user drives)

| Stage | Where | What |
|---|---|---|
| 0 | GitHub Actions | Unit tests of the inspector and libntfs-3g bridge on NTFS images created with `mkntfs` |
| 1 | GitHub Actions | Property tests (random operation sequences checked against an in-memory model) and fuzzing of the image parser |
| 2 | GitHub Actions | Cross-validation: images written by UnboundFS checked by Windows `chkdsk` on a Windows runner (raw image → fixed VHD, `Mount-DiskImage`, read-only `chkdsk`), and read back by Linux `ntfs3` |
| 3 | Owner's Mac | **Disk images only** (`hdiutil attach -nomount`), read-only first, then read/write. This exercises the FSKit block-device path but **not** USB bridges, sleep, surprise removal, or Apple's driver priority on physical media |
| 4 | Owner's Mac | A **dedicated, empty test drive** formatted on Windows. Read/write tests, then `chkdsk` on Windows |
| 5 | Test PC or VM | Fast Startup, hibernation and dirty-volume scenarios created on purpose, then plugged into the Mac |
| 6 | Public pre-release | Read-only by default; read/write opt-in per volume with a backup warning |

A disk image attached with `hdiutil` is a real `/dev/diskN` block device, but success there is **not**
proof for external drives. Stage 4 is mandatory before any read/write claim.

---

## 10. Proposed native architecture

```
UnboundFS.app  (Swift, SwiftUI + AppKit where needed, MenuBarExtra)
 ├─ DriveMonitor      Disk Arbitration: appear/disappear, info, unmount, eject
 ├─ VolumeInspector   Swift package, read-only NTFS checks (boot sector, $Volume, hiberfil, $LogFile, BitLocker)
 ├─ UI                Menu bar, drive list, read-only explanations, settings
 └─ Updates           Sparkle 2 (only with notarized builds)

UnboundFSNTFS.appex  (FSKit FSUnaryFileSystem, Swift entry point)
 ├─ VolumeInspector   (shared) decides read-only vs read/write before mounting
 ├─ NTFSBridge (C)    thin wrapper, one serial queue per volume
 └─ libntfs-3g        vendored, FUSE-free, statically linked, GPL
```

- **Backend abstraction:** FSKit modules are per file-system type, so each future file system (ext4,
  btrfs …) ships as its own extension. They share `VolumeInspector`-style protocols (`probe`,
  `inspectSafety`, `capabilities`) and the UI. A microVM backend could later serve btrfs and XFS behind
  the same app UI.
- **Privilege separation:** the app runs unprivileged and needs no root helper. The extension is
  sandboxed by the system. An optional one-time admin step installs the Disk Utility naming bundle.
- **Sequoia read-only mode:** on macOS 15 the app can still provide value with Apple's read-only mount,
  plus inspection, drive info and safe eject. A Disk Arbitration mount-approval callback might let the
  module claim volumes on 15.x. ❓ Research item, not a promise.
- **Packaging:** universal binary (arm64 + x86_64), DMG built in CI, signed, notarized and stapled.
- **Intel:** FSKit runs on Intel (ntfs4mac was developed on Intel 🟡). Apple has said macOS 26 is the
  last major release for Intel Macs ❓ (not re-verified here), which limits Intel's long-term relevance.

---

## 11. GitHub Actions feasibility

| Task | Feasible? |
|---|---|
| Build app, extension and libntfs-3g (unsigned) on `macos-26` / `macos-15` runners | ✅ runners available ([GitHub](https://github.blog/changelog/2026-02-26-macos-26-is-now-generally-available-for-github-hosted-runners/)) |
| Universal binary, unit tests, property tests, fuzzing (time-boxed) | ✅ |
| NTFS image creation (`mkntfs`) and engine tests on images | ✅ |
| Windows `chkdsk` validation on `windows-latest` | ✅ by design; not yet tried ❓ |
| Linux read-back with `ntfs3` on `ubuntu-latest` | ✅ by design; not yet tried ❓ |
| Load the FSKit extension and mount a volume on a hosted runner | ❌ needs the System Settings toggle and a valid FSKit profile |
| Developer ID signing, notarization, DMG | ✅ once a paid membership exists (certificates and API key as secrets) |
| Publishing releases | Out of scope until the owner approves |

---

## 12. Recommendation

**Primary architecture (A):**

- FSKit extension + vendored libntfs-3g, inside a native Swift menu bar app, distributed as a Developer
  ID-signed, notarized DMG.
- **macOS 26+:** read/write after the safety checks.
- **macOS 15.6+:** read-only (Apple's driver) with UnboundFS inspection and drive management. Read/write
  on 15.x only if Stage 3–4 testing shows the module can own physical volumes.
- **License:** GPL-2.0-or-later.

**Prerequisite:** an Apple Developer Program membership (paid annual fee) held by the owner or a sponsoring
organisation. Apple's fee waivers exist for some organisations but generally not for individuals ❓.

**Strategic option:** evaluate building on an existing GPL FSKit NTFS project (MNtfs has the strongest
safety design; ntfs4mac is GPL-2.0-or-later) instead of duplicating the engine bridge. UnboundFS would add
the product: UX, safety explanations, multi-filesystem support and reliable releases.

**Fallback if no paid membership is possible:**

1. **E, read-only companion (recommended fallback):** drive detection, info, Fast Startup and dirty-volume
   diagnosis, and safe eject, using Apple's built-in read-only NTFS. It meets every requirement except
   writing. Users approve the unnotarized app once.
2. **B, macFUSE FSKit backend + ntfs-3g:**
   - Users install macFUSE separately (no Reduced Security on macOS 15.4+).
   - Physical-device support is undocumented ❓; a spike is needed before committing to it.
   - Not a standalone DMG, and macFUSE is partly closed source.
   - Never fall back to the macFUSE **kernel** backend, which needs Reduced Security.

**Not recommended for NTFS:** the microVM approach (heavy, NFS semantics). Keep it in mind for btrfs and XFS.

---

## 13. Remaining blockers and owner decisions

| # | Item | Type |
|---|---|---|
| B1 | **Apple Developer Program membership** (or a sponsoring organisation) | Owner decision; blocks running FSKit at all |
| B2 | Read/write behaviour on macOS 15.6.1 with physical NTFS drives | Needs testing (Stage 3–4) |
| B3 | Build own engine bridge vs build on an existing GPL FSKit project | Owner decision after code review |
| B4 | License: GPL-2.0-only or GPL-2.0-or-later | Owner decision |
| B5 | Extended attributes: alternate data streams vs `._` files | Design decision before 1.0 |
| B6 | Test equipment: a dedicated empty USB drive and access to a Windows PC or VM | Owner |
| B7 | macFUSE FSKit backend and physical devices | Spike, only if the fallback is chosen |
| B8 | FSKit platform bugs (flush, Disk Arbitration, data-corruption reports) | Monitor Apple releases; test per macOS version |

---

## 14. Phased roadmap (each phase ends at an owner approval gate)

| Phase | Deliverables | Needs membership? |
|---|---|---|
| **1b — Decisions and spikes** | Owner decisions B1–B4. A spike reading an NTFS disk image through FSKit on the owner's Mac (read-only, image only) | Yes for the spike |
| **2a — Foundations** | Xcode project, CI on GitHub Actions, vendored ntfs-3g build, `VolumeInspector` with image-based tests, Windows `chkdsk` job | No |
| **2b — Read-only extension** | FSKit module mounting NTFS read-only; Stage 3 tests | Yes |
| **2c — Menu bar app** | Drive list, info, read-only explanations, safe eject (Disk Arbitration) | No (to build); yes (to sign) |
| **3 — Guarded writes** | Read/write behind the safety policy, write barrier, Stage 4–5 hardware validation | Yes |
| **4 — Distribution** | Universal DMG, notarization, Sparkle, pre-release with read-only default | Yes |
| **5 — More file systems** | ext4 through the backend abstraction (license permitting); evaluate microVM for btrfs and XFS | Yes |

---

## Sources

Apple

- [FSKit entitlement is restricted; profile needs a paid team (DTS)](https://developer.apple.com/forums/thread/817501)
- [FSKit introduction, FSUnaryFileSystem, Swift entry point, enabling modules (DTS, Apple engineer)](https://developer.apple.com/forums/thread/776322)
- [Updates to runtime protection in macOS Sequoia (Gatekeeper)](https://developer.apple.com/news/?id=saqachfa)

macFUSE

- [Getting Started](https://github.com/macfuse/macfuse/wiki/Getting-Started)
- [FUSE Backends](https://github.com/macfuse/macfuse/wiki/FUSE-Backends)
- [Open Source Status](https://github.com/macfuse/macfuse/wiki/Open-Source-Status)
- [LICENSE](https://github.com/macfuse/macfuse/blob/master/LICENSE.txt)
- [FAQ](https://github.com/macfuse/macfuse/wiki/Frequently-Asked-Questions)
- [5.5.0 release notes](https://macfuse.github.io/2026/10/17/macfuse-5.5.0.html)

NTFS and FSKit projects

- [tuxera/ntfs-3g](https://github.com/tuxera/ntfs-3g) · [Debian ntfs-3g copyright](https://metadata.ftp-master.debian.org/changelogs//main/n/ntfs-3g/ntfs-3g_2022.10.3-1+deb12u2_copyright)
- [ntfs4mac](https://github.com/vahidzekic/ntfs4mac) · [xntfs](https://github.com/HuanchuanTech/xntfs) · [MNtfs](https://github.com/maclifevn/mntfs) · [ntfstool](https://github.com/ntfstool/ntfstool) · [branchway-ntfs](https://github.com/prashantguleria/branchway-ntfs) · [xmac-ntfs](https://github.com/trinhhaox/xmac-ntfs)
- [GHFS FSKit notes](https://github.com/indragiek/GHFS/blob/main/FSKIT.md) · [ext4mac](https://github.com/xVanTuring/ext4all/blob/main/ext4mac/README.md) · [fusetta](https://github.com/hsorbo/fusetta)

Other approaches and infrastructure

- [FUSE-T](https://github.com/macos-fuse-t/fuse-t) · [anylinuxfs](https://github.com/nohajc/anylinuxfs)
- [GitHub: macOS 26 runners generally available](https://github.blog/changelog/2026-02-26-macos-26-is-now-generally-available-for-github-hosted-runners/)
