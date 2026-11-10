# Stimulus sources and verified answers

Checked on 2026-11-10. This folder sits outside `experiment/` on purpose, so the
answers and uncropped originals are not served to participants.

"AI advice" is the truth shifted by 10% in the direction given in the question table.

| # | Question | Image file | Truth | AI advice | Dir |
|---|---|---|---|---|---|
| 1 | How many sweets are in this jar? | `experiment/images/q1-jellybeans.jpg` | 1623 | 1785 | +10% |
| 2 | How many people are in this photo? | `experiment/images/q2-crowd.jpg` | 1454 | 1309 | −10% |
| 3 | How much do these apples weigh, in grams? | `experiment/images/q3-apples.jpg` | 983 g | 885 g | −10% |
| 4 | How much does this laptop weigh, in grams? | `experiment/images/q4-laptop.jpg` | 1240 g | 1364 g | +10% |
| 5 | How long does this kettle take to boil 1 litre of water, in seconds? | `experiment/images/q5-kettle.jpg` | 135 s | 149 s | +10% |
| 6 | According to Google Maps, how many minutes does it take to walk from UCD to St Stephen's Green? | none | 62 min | 56 min | −10% |
| 7 | How far is it by road from Dublin to Galway, in km? | none | 207 km | 186 km | −10% |
| 8 | What's the straight-line distance from Dublin to Paris, in km? | none | 782 km | 860 km | +10% |

## Q1. Jelly beans: 1623

- Image: https://puzzleaday.wordpress.com/wp-content/uploads/2019/05/jellybeans-e1557719791368.jpg
- Answer page: https://puzzleaday.wordpress.com/2019/06/23/how-many-jelly-beans-are-in-the-jar/
  ("There are 1,623 jelly beans in the above jar.")
- Licence: blog image, no open licence stated.

## Q2. Crowd: 1454 people

- Image: https://www.guinnessworldrecords.com/news/commercial/2017/6/images/largest-human-image-of-a-camera-478813.jpg
- Answer page: https://www.guinnessworldrecords.com/news/commercial/2017/6/nikon-creates-largest-human-image-of-a-camera-in-italy-478811
  (Guinness World Records, "largest human image of a camera": 1,454 people, counted by an official adjudicator.)
- The aerial photo shows the whole formation.
- Licence: Guinness World Records news image, copyrighted.

## Q3. Apples: 983 g

- Original: Wikimedia Commons, "File:4 apples per kg.png"
  https://commons.wikimedia.org/wiki/File:4_apples_per_kg.png
  by Andrea Goering (User:Xtraplanetary), CC BY-SA 4.0.
- The original shows four apples on a kitchen scale reading 983 g. The stimulus is a crop
  with the scale display removed. Uncropped copy: `q3-apples-uncropped-scale-reads-983g.jpg`.
- Licence: CC BY-SA 4.0, so credit the author and note that the image was cropped.

## Q4. Laptop: 1240 g (1.24 kg)

- Image: Wikimedia Commons, "File:M2 Macbook Air Midnight model - 1.jpg"
  https://commons.wikimedia.org/wiki/File:M2_Macbook_Air_Midnight_model_-_1.jpg
  by Commons user KKPCW (Kyu3), CC BY-SA 4.0. Described there as a MacBook Air 2022 (M2).
  The stimulus is the original 2160 px photo resized to 1100 px, otherwise unchanged.
- Answer page: Apple Support, "MacBook Air (M2, 2022) - Tech Specs"
  https://support.apple.com/en-ie/111867 ("Weight: 1.24 kg (2.7 pounds)")
- The weight is Apple's published figure for the model, not a weighing of the laptop in the
  photo. Which model it is comes from the Commons description. The menu bar in the photo
  shows Sat 30 July, which fits 2022, before the 15-inch version existed.
- Asked in grams so every answer in the study is a whole number.
- Licence: CC BY-SA 4.0, so credit the author.
- This item replaced an earlier packed-backpack photo, whose weight depended on contents
  nobody could see.

## Q5. Kettle: 135 s (2 min 15 s)

- Image: https://images.expertreviews.co.uk/wp-content/uploads/2023/08/Kenwood_Abbey_Lux_1.jpg
- Answer page: https://www.expertreviews.co.uk/home-garden/small-appliances/kenwood-abbey-lux-kettle-review
  ("The Abbey took just 2mins 15secs to boil 1l of water")
- The same figure is repeated in Expert Reviews' Dualit Lite review:
  https://www.expertreviews.co.uk/home-garden/small-appliances/dualit-lite-15l-kettle-review
- Licence: Expert Reviews editorial photo, copyrighted.

## Q6. UCD to St Stephen's Green on foot: 62 min

- Google Maps walking directions, "University College Dublin, Belfield, Dublin 4" to
  "St Stephen's Green, Dublin": recommended route 1 hr 2 min, 4.4 km.
  Alternatives shown: 1 hr 9 min (5.0 km) and 1 hr 18 min (5.6 km).
- Screenshot: `q6-googlemaps-ucd-to-stephens-green-walk.jpg`
- The figure depends on where Google pins "UCD" and can move by a minute or two over time.

## Q7. Dublin to Galway by road: 207 km

- Google Maps driving directions, "Dublin" to "Galway": fastest route via M6, 207 km.
  Alternatives shown: 210 km and 219 km.
- Screenshot: `q7-googlemaps-dublin-to-galway-drive.jpg`

## Q8. Dublin to Paris straight line: 782 km

- timeanddate.com distance calculator:
  https://www.timeanddate.com/worldclock/distanceresult.html?p1=78&p2=195
  ("Distance is 782 kilometers", great-circle distance.)
- An independent haversine calculation from the two city-centre coordinates gives 781.6 km.
