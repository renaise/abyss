# Sources

All input images are public-domain (CC0 1.0) objects released by The Metropolitan Museum of Art under its
Open Access policy. Each object was checked on 2026-11-02 (ET) with the Met Collection API
(`/public/collection/v1/objects/<id>` returned `isPublicDomain: true`). Originals were downloaded from the
`primaryImage` URL, converted to RGB, downscaled with Lanczos to a longest side of at most 1536 px and saved as PNG
(no metadata kept). No people photographed, no logos, no client material.

CC0 terms: https://creativecommons.org/publicdomain/zero/1.0/ ; Met Open Access policy:
https://www.metmuseum.org/policies/image-resources

| File | Object | Met object page | Original image | Original SHA-1 | License |
|---|---|---|---|---|---|
| `inputs/hippo.png` (1151x1536, from 2899x3870 JPEG) | Hippopotamus ("William"), ca. 1961–1878 B.C.. Egypt, Middle Kingdom. Acc. no. 17.9.1 | https://www.metmuseum.org/art/collection/search/544227 | https://images.metmuseum.org/CRDImages/eg/original/DP248993.jpg | `a53d057d6842838f61be07139232e5c4adb25b8c` | CC0 1.0 (Met Open Access, `isPublicDomain: true` via the Met Collection API) |
| `inputs/netsuke.png` (1536x1024, from 4000x2667 JPEG) | Netsuke, 18th century. Japan. Acc. no. 10.211.2273 | https://www.metmuseum.org/art/collection/search/59356 | https://images.metmuseum.org/CRDImages/as/original/LC-10_211_2273_001.jpg | `a5ea2f69ab42f61c4dad1c50d9eee08049cdb67a` | CC0 1.0 (Met Open Access, `isPublicDomain: true` via the Met Collection API) |

Generated outputs are listed in the Examples section of `README.md`.
