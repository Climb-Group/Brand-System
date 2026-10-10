# Photography

For event photographers, designers choosing images and anyone briefing a shoot. Photography carries most of the festival feel: the type and colour are the poster, the photos are the reason to come.

## What to shoot

- **Joy and connection:** people laughing, leaning in, shaking hands mid-conversation, a group selfie at the deckchair. Real reactions, not posed lines.
- **Main Stage Moments:** the speaker mid-gesture with the branded backdrop behind, the crowd looking up, the band opening day one, the ClimbAwards walk-up.
- **Find Your People:** close conversations on the expo floor, Investor Speed Networking tables, roundtables in full flow.
- **The texture of the festival:** orange lanyards, badges, the photo wall, drinks being poured, trophies lined up, the food trucks, the after party lights.
- **Wide establishing shots** of a full room or a busy floor, one or two per day. Never an empty room.

## How it should look

- Full colour, warm and bright. Keep the stage-light orange and the warmth of the room; do not desaturate or cool it down.
- Shallow depth of field for people (f/1.8 to f/2.8), so the subject pops and the background becomes colour and light.
- Faces in focus, eyes lit. Catch the moment just before or just after the laugh.
- Variety: for every wide, shoot three mediums and five close-ups. Landscape for the web and slides, portrait for stories and phone heroes.

## Editing

- One consistent edit across an edition: warm white balance, lifted shadows that lean Dark Brown, natural skin, orange held saturated.
- Light retouching only (stray hairs, a blemish, a distracting exit sign). Never change who was there or what happened.
- **Resolution:** always the highest the camera allows. Shoot RAW at no less than 4K (3840px on the long edge); 6K is fine and 8K is ideal and never crop a delivered image below 3840px on its long edge.
- Deliver the RAW files plus full-resolution sRGB JPGs at quality 90. Web and social copies are exported from the full-resolution file at the size each placement needs, never upscaled.
- File names: `<edition>_<day>_<moment>_<photographer>_<number>.jpg`, for example `climb27_d1_main-stage_jsmith_0142.jpg`.

## Using photos in designs

- **Text over a photo** sits on a Dark Brown fade (left to right, or bottom up), not a flat grey box. See "Photo fades" below for the recipes.
- **Photo cards:** title at the top, a line at the bottom, a Dark Brown fade top and bottom, rounded `radius-card` corners.
- **Photo walls:** a mosaic of squares with one big tile. Dense is better than sparse.
- **Crop** for the face and the gesture; leave room on one side for the headline.
- One photo per hero. No collages inside a hero, no cut-out people, no duotones that hide faces.
- Alt text describes what is happening ("A brass band playing on the main stage"), following the Voice section.

## Photo fades

The fade is what makes a photo section feel like a festival: the photo fills the width, the words sit on a warm dark side, and the photo shows through on the other. Ink is Dark Brown `rgb(30 15 5)`, orange is Climb Orange `rgb(232 113 42)`. Layer the gradients over the photo in the order given (first on top).

| Fade | Use it for | Layers |
|---|---|---|
| **Brown** | Statements and story bands ("Business with a party"), with photo cards below | `linear-gradient(90deg, ink 90%, ink 60% at 55%, ink 45%)`, then `linear-gradient(180deg, ink 50%, ink 20% at 50%, ink 100%)` |
| **Heat** | Ticket moments: a line, two buttons | `linear-gradient(90deg, ink 92%, ink 70% at 45%, orange 35%)`, then `radial-gradient(60rem 30rem at 85% 110%, orange 55%, transparent 60%)`, then `linear-gradient(180deg, ink 35%, ink 0% at 45%, ink 70%)` |
| **Orange** | One offer on a Climb Orange section (team tickets, a deadline) | `linear-gradient(90deg, orange 97%, orange 90% at 50%, orange 50%)`, then a white light `radial-gradient(40rem 20rem at 10% 0%, white 20%, transparent 60%)` |
| **Hero** | The first screen | `linear-gradient(180deg, ink 35%, ink 15% at 40%, ink 97%)`, then `linear-gradient(100deg, ink 94%, ink 72% at 45%, ink 25%)`, then the orange glow `radial-gradient(60rem 30rem at 85% 110%, orange 28%, transparent 60%)` |
| **Card** | Photo cards with text top and bottom | `linear-gradient(180deg, ink 88%, ink 55% at 30%, ink 38% at 50%, ink 94%)` |

Percentages after a colour are its opacity; "at" gives the stop position.

- **Words sit on the dark side.** Text goes where the fade is at least 85% ink (or 90% orange), so contrast never depends on the photo. Check the darkest and the lightest part of the photo behind the words.
- **End on solid.** A band that runs into cards or the next dark section ends at 100% ink, so there is no seam.
- **Orange fades go over things and places,** never over faces: a crowd seen from behind, the stage, the trophies, the bar. Faces stay natural under a brown fade.
- **On orange,** the headline is white and large (24px, or 19px bold) with one Dark Brown word; the button is Dark Brown.
- Flip the direction (270deg) when the words sit on the right.

## Consent and care

- The event's filming notice covers general crowd photography. Anyone in a close-up used in marketing has agreed, and anyone who asks to be removed is removed from the library and every live use.
- Honour opt-out lanyards or badges, and never photograph screens with attendee data.
- Credit the photographer where the channel allows.

## Never

- Stock photos of handshakes, skylines, laptops or diverse-team-pointing-at-a-screen.
- Empty rooms, half-built stands, or rows of empty chairs.
- Photos that make the festival look like a conference: lecterns from the back, slides with no people, lanyards on a table.
