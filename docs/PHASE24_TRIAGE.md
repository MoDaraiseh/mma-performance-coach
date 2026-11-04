# Phase 24 vulnerability triage matrix

Historical scanner/advisory snapshot. See [the authoritative final handoff](FINAL_DELIVERY.md) for updated musl vendor-patch evidence and remaining security gates. No historical finding has been suppressed.

72 image/finding rows; 69 distinct high/critical CVEs. Covers every baseline high/critical finding and high/critical findings introduced by the evaluated Alpine variant. No exceptions are approved.

Full versions, affected locations, vendor/CNA boundaries, reachability evidence, compensating controls, remaining risks and approval requirements are in [JSON](evidence/phase24/triage-matrix.json) and [CSV](evidence/phase24/triage-matrix.csv). Authoritative CNA records were retrieved on 2026-11-01; original descriptions and references are retained privately under `.qa-runtime/phase24/advisories`.

The cached scanner labels are preserved. Presence of an old Go version does not prove each linked library routine is used by gosu. Removal is verified independently, rather than treating speculation as a security exception. Windows-specific Go findings are platform-inapplicable on the Linux runtime. The final PostgreSQL libxml2 finding remains unresolved.

## baseline-app

| CVE / severity | Component / installed | Final candidate and decision |
| --- | --- | --- |
| [CVE-2026-53613](https://cveawg.mitre.org/api/cve/CVE-2026-53613) / HIGH | util-linux 2.38.1-5+deb12u3 | Affected util-linux mount/nsenter/libblkid absent; only libuuid 2.42.3-r1 retained with Alpine security fixes; Affected component replaced/absent in candidate |
| [CVE-2026-84243](https://cveawg.mitre.org/api/cve/CVE-2026-84243) / HIGH | glibc 2.36-9+deb12u14 | Absent as affected source package (musl/BusyBox runtime); Affected component replaced/absent in candidate |
| [CVE-2026-82560](https://cveawg.mitre.org/api/cve/CVE-2026-82560) / HIGH | perl 5.36.0-7+deb12u4 | Absent as affected source package (musl/BusyBox runtime); Likely package-level false positive: affected Pod::Text module absent; security confirmation pending |
| [CVE-2026-78410](https://cveawg.mitre.org/api/cve/CVE-2026-78410) / HIGH | util-linux 2.38.1-5+deb12u3 | Affected util-linux mount/nsenter/libblkid absent; only libuuid 2.42.3-r1 retained with Alpine security fixes; Affected component replaced/absent in candidate |
| [CVE-2026-78408](https://cveawg.mitre.org/api/cve/CVE-2026-78408) / HIGH | util-linux 2.38.1-5+deb12u3 | Affected util-linux mount/nsenter/libblkid absent; only libuuid 2.42.3-r1 retained with Alpine security fixes; Affected component replaced/absent in candidate |
| [CVE-2026-53615](https://cveawg.mitre.org/api/cve/CVE-2026-53615) / HIGH | util-linux 2.38.1-5+deb12u3 | Affected util-linux mount/nsenter/libblkid absent; only libuuid 2.42.3-r1 retained with Alpine security fixes; Affected component replaced/absent in candidate |
| [CVE-2026-85091](https://cveawg.mitre.org/api/cve/CVE-2026-85091) / HIGH | zlib 1:1.2.13.dfsg-1 | zlib 1.3.2-r1; Alpine secfixes lists this CVE fixed; Vendor-patched candidate; original distro/upstream range discrepancy retained |
| [CVE-2026-76642](https://cveawg.mitre.org/api/cve/CVE-2026-76642) / HIGH | util-linux 2.38.1-5+deb12u3 | Affected util-linux mount/nsenter/libblkid absent; only libuuid 2.42.3-r1 retained with Alpine security fixes; Affected component replaced/absent in candidate |

## baseline-postgres

| CVE / severity | Component / installed | Final candidate and decision |
| --- | --- | --- |
| [CVE-2026-84243](https://cveawg.mitre.org/api/cve/CVE-2026-84243) / HIGH | glibc 2.41-12+deb13u4 | Absent as affected source package (musl/BusyBox runtime); Affected component replaced/absent in candidate |
| [CVE-2025-58187](https://cveawg.mitre.org/api/cve/CVE-2025-58187) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2025-58188](https://cveawg.mitre.org/api/cve/CVE-2025-58188) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2025-61723](https://cveawg.mitre.org/api/cve/CVE-2025-61723) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2025-61725](https://cveawg.mitre.org/api/cve/CVE-2025-61725) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2025-61726](https://cveawg.mitre.org/api/cve/CVE-2025-61726) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2025-61729](https://cveawg.mitre.org/api/cve/CVE-2025-61729) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-25679](https://cveawg.mitre.org/api/cve/CVE-2026-25679) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-32280](https://cveawg.mitre.org/api/cve/CVE-2026-32280) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-32281](https://cveawg.mitre.org/api/cve/CVE-2026-32281) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-32283](https://cveawg.mitre.org/api/cve/CVE-2026-32283) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-33811](https://cveawg.mitre.org/api/cve/CVE-2026-33811) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-33814](https://cveawg.mitre.org/api/cve/CVE-2026-33814) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-33818](https://cveawg.mitre.org/api/cve/CVE-2026-33818) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-39820](https://cveawg.mitre.org/api/cve/CVE-2026-39820) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-39836](https://cveawg.mitre.org/api/cve/CVE-2026-39836) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-42499](https://cveawg.mitre.org/api/cve/CVE-2026-42499) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-42504](https://cveawg.mitre.org/api/cve/CVE-2026-42504) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-56853](https://cveawg.mitre.org/api/cve/CVE-2026-56853) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-56859](https://cveawg.mitre.org/api/cve/CVE-2026-56859) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-56862](https://cveawg.mitre.org/api/cve/CVE-2026-56862) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-56866](https://cveawg.mitre.org/api/cve/CVE-2026-56866) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-78659](https://cveawg.mitre.org/api/cve/CVE-2026-78659) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-78660](https://cveawg.mitre.org/api/cve/CVE-2026-78660) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-78667](https://cveawg.mitre.org/api/cve/CVE-2026-78667) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-78669](https://cveawg.mitre.org/api/cve/CVE-2026-78669) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-94439](https://cveawg.mitre.org/api/cve/CVE-2026-94439) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-94440](https://cveawg.mitre.org/api/cve/CVE-2026-94440) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-97031](https://cveawg.mitre.org/api/cve/CVE-2026-97031) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-97032](https://cveawg.mitre.org/api/cve/CVE-2026-97032) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-39822](https://cveawg.mitre.org/api/cve/CVE-2026-39822) / HIGH | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-86140](https://cveawg.mitre.org/api/cve/CVE-2026-86140) / HIGH | libxml2 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | libxml2 2.13.9-r2; Unresolved affected library; upstream fixed 2.15.4, no v3.24 package fix |
| [CVE-2026-85091](https://cveawg.mitre.org/api/cve/CVE-2026-85091) / HIGH | zlib 1:1.3.dfsg+really1.3.1-1 | zlib 1.3.2-r1; Alpine secfixes lists this CVE fixed; Vendor-patched candidate; original distro/upstream range discrepancy retained |
| [CVE-2026-74860](https://cveawg.mitre.org/api/cve/CVE-2026-74860) / HIGH | libxml2 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | libxml2 2.13.9-r2; Binding-specific finding; additional evidence required for original; not reported in final scan |
| [CVE-2026-78663](https://cveawg.mitre.org/api/cve/CVE-2026-78663) / CRITICAL | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-39821](https://cveawg.mitre.org/api/cve/CVE-2026-39821) / CRITICAL | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2026-56857](https://cveawg.mitre.org/api/cve/CVE-2026-56857) / CRITICAL | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |
| [CVE-2025-68121](https://cveawg.mitre.org/api/cve/CVE-2025-68121) / CRITICAL | Go stdlib 1.24.6 | Absent: gosu and all Go packages removed from merged artifact; Component removed; no exception required for candidate |

## alpine-postgres-before-patches

| CVE / severity | Component / installed | Final candidate and decision |
| --- | --- | --- |
| [CVE-2026-87865](https://cveawg.mitre.org/api/cve/CVE-2026-87865) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-86415](https://cveawg.mitre.org/api/cve/CVE-2026-86415) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-92390](https://cveawg.mitre.org/api/cve/CVE-2026-92390) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-92391](https://cveawg.mitre.org/api/cve/CVE-2026-92391) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-94266](https://cveawg.mitre.org/api/cve/CVE-2026-94266) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-86140](https://cveawg.mitre.org/api/cve/CVE-2026-86140) / HIGH | libxml2 2.13.9-r2 | libxml2 2.13.9-r2; Unresolved affected library; upstream fixed 2.15.4, no v3.24 package fix |
| [CVE-2026-107928](https://cveawg.mitre.org/api/cve/CVE-2026-107928) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-107929](https://cveawg.mitre.org/api/cve/CVE-2026-107929) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-86409](https://cveawg.mitre.org/api/cve/CVE-2026-86409) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-86410](https://cveawg.mitre.org/api/cve/CVE-2026-86410) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-86412](https://cveawg.mitre.org/api/cve/CVE-2026-86412) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-87862](https://cveawg.mitre.org/api/cve/CVE-2026-87862) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-87863](https://cveawg.mitre.org/api/cve/CVE-2026-87863) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-87864](https://cveawg.mitre.org/api/cve/CVE-2026-87864) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-92386](https://cveawg.mitre.org/api/cve/CVE-2026-92386) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-92387](https://cveawg.mitre.org/api/cve/CVE-2026-92387) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-92389](https://cveawg.mitre.org/api/cve/CVE-2026-92389) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-92392](https://cveawg.mitre.org/api/cve/CVE-2026-92392) / HIGH | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-86411](https://cveawg.mitre.org/api/cve/CVE-2026-86411) / CRITICAL | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-86413](https://cveawg.mitre.org/api/cve/CVE-2026-86413) / CRITICAL | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-86414](https://cveawg.mitre.org/api/cve/CVE-2026-86414) / CRITICAL | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-87861](https://cveawg.mitre.org/api/cve/CVE-2026-87861) / CRITICAL | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-87866](https://cveawg.mitre.org/api/cve/CVE-2026-87866) / CRITICAL | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-92388](https://cveawg.mitre.org/api/cve/CVE-2026-92388) / CRITICAL | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-94265](https://cveawg.mitre.org/api/cve/CVE-2026-94265) / CRITICAL | curl 8.22.0-r0 | libcurl 8.23.0-r0; Verified exact package upgrade; absent from final scanner findings |
| [CVE-2026-111497](https://cveawg.mitre.org/api/cve/CVE-2026-111497) / CRITICAL | brotli 1.2.0-r1 | brotli-libs 1.2.1-r0; Verified exact package upgrade; absent from final scanner findings |

## Unresolved candidate advisories

- **CVE-2026-86140, high:** libxml2 2.13.9-r2 in PostgreSQL. Upstream 2.15.4 addresses it; the current Alpine 3.24 repository offers no newer libxml2. XML support is linked and SQL XML parsing works. The vulnerable validation path has not been proven unreachable. Retain as an open security gate; require a supported vendor backport/new image and separate regression, or explicit reviewed risk acceptance. No acceptance has been granted.
- **CVE-2026-107891, unspecified:** scanner requires musl 1.2.6-r6, but current Alpine 3.24 secfixes says fixed in installed 1.2.6-r3; repository latest is r3. The authoritative CVE API returned 404. Treat as a vendor/scanner data discrepancy requiring resolution, not a confirmed clean result or automatic false-positive exception. Affects both application and PostgreSQL candidates.
- Final PostgreSQL scan also reports five medium and five low libxml2 findings. They remain reported in SARIF; they are not suppressed.
- Existing port 18018 staging still uses original images and all its prior findings. Candidate improvements do not remediate that preserved environment.
