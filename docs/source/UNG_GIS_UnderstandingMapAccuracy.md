---
title: "Understanding Map Accuracy"
subtitle: "Why Maps Don't Always Agree — and Which One to Trust"
author: "John Segars, MGIS"
organization: "University of North Georgia — Enterprise GIS Program, Facilities Planning"
division: "Facilities"
date: "2026"
version: "1.0"
audience: "Facilities Staff, Project Managers, and Campus Partners"
---

# Understanding Map Accuracy
**Why Maps Don't Always Agree — and Which One to Trust**

*UNG Facilities GIS | University of North Georgia | A Guide for Facilities Staff, Project Managers, and Campus Partners | 2026*

---

If you have ever looked at a campus map and noticed that a building, road, or utility line does not quite line up with what you see on Google Maps or another satellite image, you are not imagining things. Maps disagree with each other all the time — even maps produced by professional organizations using sophisticated equipment.

This document explains why that happens, what it means for how you use GIS data, and which sources you should trust for which purposes.

> **"The satellite image looks right to me — why doesn't the GIS data match it?"**
> This is the most common question facilities staff ask about campus mapping. The honest answer: the satellite image may not be as accurate as it looks.

---

## 1. Why Satellite and Aerial Images Are Not Perfect Maps

Photographs taken from aircraft or satellites look like maps, but they are not the same thing. A raw aerial photograph captures light reflected off the ground from a single point in the sky at a single moment in time. Because the camera is never perfectly overhead every part of the scene, objects that have height — buildings, trees, light poles — appear to lean away from the center of the image. This is called **relief displacement**.

Professionals correct for this by processing the photograph through a series of mathematical steps using terrain data and known reference points on the ground. The result is called an **orthophoto** — a photograph corrected to approximate a true map view. But the correction is only as good as the terrain data and reference points used, and it is never perfect.

The practical consequence: a tall building photographed from an aircraft will show its rooftop shifted horizontally from its true ground footprint. Depending on the building height and the camera angle, that shift can be 5 to 15 feet or more. If you click on a building corner in a satellite image to place something on a map, you may be clicking on the roof edge — not the foundation — and your map feature lands in the wrong place without any visible indication that something went wrong.

### What About Google Maps and Bing?

Consumer mapping services like Google Maps, Bing Maps, and Apple Maps are assembled from many different imagery sources collected at different times by different providers. The individual image tiles are stitched together and the seams are smoothed, but the underlying positional accuracy varies considerably from tile to tile. In some areas Google Maps is accurate to within a few feet. In other areas — including many institutional campuses and rural areas — offsets of 10 to 30 feet are not unusual.

Google and Microsoft do not publish accuracy specifications for their basemap imagery because accuracy varies by location and changes as imagery is updated. This means you cannot know how accurate a particular area of Google Maps is without comparing it to a known reference — which defeats the purpose of using it as a reference.

---

## 2. Why Different Maps Disagree With Each Other

When you display two map layers together and they do not line up, it does not necessarily mean either one is wrong in an absolute sense. It usually means they were produced using different methods, different reference points, or different assumptions — and each has its own positional error relative to the true location on the ground.

**Common reasons maps disagree:**

- **Different collection dates.** A building demolished in 2018 may still appear in imagery collected in 2016. A road realigned in 2022 may appear in its old location on an older basemap.
- **Different ground control.** Every survey or aerial photography project uses a network of known reference points to anchor the data to real-world coordinates. Different projects use different reference networks, producing slightly different results.
- **Different correction methods.** Some imagery is corrected using detailed terrain models; some uses coarser approximations. The quality of terrain correction directly affects horizontal accuracy.
- **Different coordinate system interpretations.** Coordinate systems have evolved over decades and the same coordinate values can represent slightly different physical locations depending on which version of a coordinate system was used. Differences of 1 to 3 feet are common between older and newer realizations of the same system.
- **Different accuracy standards.** A professionally surveyed construction drawing is held to a legal accuracy standard measured in tenths of a foot. A consumer satellite basemap has no published accuracy standard at all. Both look equally convincing on screen.

The important takeaway is that visual agreement between two map layers does not mean either one is accurate — it may simply mean they were derived from the same source and inherited the same errors together.

---

## 3. Which Map Source Should I Trust?

Not all map sources are equal. The table below shows the sources used in UNG's campus GIS program ranked from most to least positionally reliable, along with guidance on appropriate uses for each.

| Source Type | Typical Accuracy | Appropriate Uses | Not Appropriate For |
|---|---|---|---|
| Licensed survey documents with explicit coordinates | 0.1 – 0.5 ft | Legal boundaries, utility as-built locations, ADA compliance, construction planning | Nothing — this is the highest confidence source available |
| Survey-grade GPS collected in the field | 0.1 – 1.0 ft | Feature location, infrastructure inventory, field verification | Legal boundary determination without licensed surveyor |
| Professional LIDAR orthophoto (UNG campus flight) | 1 – 3 ft | General campus mapping, building footprints, terrain analysis | Precise utility location, construction stakeout |
| State or county orthophotos | 3 – 10 ft | General reference, change detection, context mapping | Feature placement requiring better than 5 ft accuracy |
| Google Maps / Bing / Esri World Imagery | 5 – 30 ft (varies, unspecified) | Visual orientation, general context, public-facing maps | Any technical decision requiring known accuracy; never as georeferencing control |

---

## 4. Common Questions

**Q: A utility line on the campus GIS map doesn't match where I see it on Google Maps. Which is right?**

A: It depends on the source of the GIS feature. If the utility line was captured from a licensed survey drawing with coordinate-explicit control points, the GIS data is almost certainly more accurate than Google Maps. If it was digitized by clicking on an aerial image, the answer is less clear. Check the data source documentation for that feature class — the GIS program maintains records of how each dataset was produced and what accuracy level it carries. When in doubt, field verification is always the authoritative answer.

---

**Q: A contractor is telling me our GIS data is wrong because it doesn't match their GPS unit. Who is right?**

A: Modern consumer and survey-grade GPS units can be very accurate, but accuracy depends on occupation time, satellite geometry, equipment calibration, and correction method. A contractor using a sub-meter GPS with real-time correction in an open area can achieve 1 to 3 foot accuracy. A contractor using a phone-based GPS app may have 15 to 30 foot error. Ask what equipment was used and what the stated accuracy is. If the contractor has survey-grade data and a clear discrepancy with UNG's GIS, that is worth investigating. If they are comparing to a phone or consumer device, the GIS data is more likely correct.

---

**Q: Can I use the campus GIS map to locate an underground utility before digging?**

A: No — and this is critically important. GIS maps of underground utilities show approximate locations based on as-built drawings, georeferenced construction documents, and historical records. They are not survey-grade and should never be used as the sole reference for excavation. Always call 811 before any digging, and always field-verify utility locations with appropriate detection equipment. The GIS data is useful for planning and awareness — not for safe excavation without additional verification.

---

**Q: Why does the campus GIS sometimes show buildings slightly offset from the satellite image?**

A: The campus GIS building footprints were captured from professional sources including survey drawings and LIDAR data. The satellite basemap displayed beneath the GIS layers is a consumer product with unspecified positional accuracy that varies by location. When there is a discrepancy, the GIS building footprint is generally more reliable than the basemap imagery. The imagery is there for visual context, not as a positional reference.

---

**Q: How accurate is accurate enough for my project?**

A: That depends entirely on what decisions the map will support. A general planning map showing which buildings are on which campus needs only rough accuracy. A map used to design a drainage system needs survey-grade vertical accuracy. A map used to determine ADA compliance on a walkway needs sub-foot accuracy. Before using GIS data for any technical decision, ask the GIS program what accuracy level that dataset carries and whether it is sufficient for your purpose. The GIS staff would rather have that conversation before a project begins than after a problem is discovered.

---

## 5. UNG GIS Data Accuracy Tiers

UNG's GIS program uses three accuracy tiers to classify spatial data. It is important to understand that the majority of current campus GIS data falls into **Tier 3** — built incrementally from historical records, as-built drawings, and heads-up digitizing over many years before formal accuracy standards were in place. A smaller portion reaches Tier 2 through georeferenced construction documents and professional imagery. Tier 1 data is limited to features captured directly from coordinate-explicit survey sources. Improving data accuracy across the program is an active and ongoing priority. When you receive a map or data layer from the GIS program, you can ask which tier applies to the features you are using.

| Tier | Name | Horizontal Accuracy | Typical Source | Suitable For |
|---|---|---|---|---|
| 1 | Survey Grade | Sub-foot (< 1 ft) | Licensed survey documents with explicit coordinates; survey-grade GPS | Legal decisions, construction planning, ADA compliance, utility design |
| 2 | GIS Grade | 1 – 5 feet | Georeferenced construction documents; professional orthophotos; quality GPS | Facilities planning, space inventory, infrastructure awareness mapping |
| 3 | Approximate | 5+ feet | Heads-up digitizing from consumer imagery; historical records; field sketches | General reference only; not for technical decisions without field verification |

Documenting the accuracy tier of every GIS feature class is a program goal actively being worked toward. In the meantime, if you are unsure what accuracy level applies to a dataset you are using, contact the GIS program before making decisions that depend on positional accuracy.

---

## 6. A Note on 811 and Underground Utilities

> **Always call 811 before any excavation — regardless of what any map shows.**
>
> GIS utility maps are planning tools. They are not a substitute for utility locating services. Underground infrastructure can shift, be abandoned in place, be installed without documentation, or be mapped with positional error that looks small on screen but is large enough to cause a serious incident in the field. No map — including this one — eliminates the requirement to call 811 and have utilities physically located before ground disturbance of any kind.

---

*University of North Georgia Enterprise GIS Program — Facilities Planning Division. Questions about data accuracy, appropriate use, or data requests should be directed to the GIS Analyst / Facilities Planning Specialist. This document is intended for general campus audiences and does not constitute legal or engineering advice.*
