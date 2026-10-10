/** ClimbUK components: plain HTML and CSS, no framework. Load tokens.css and bundle.css, then bundle.js. */
export interface ClimbComponentProps {
  /** Force a theme; default follows <html data-theme>. */
  theme?: 'dark' | 'light';
}
export interface ClimbComponent {
  (props?: ClimbComponentProps): HTMLElement;
  /** The component's markup. */
  html: string;
  group: string;
  summary: string;
  title: string;
}
/** The five grounds, each with its own text, link and button colours */
export type PresetsProps = ClimbComponentProps;
/** Uppercase display lines with one orange word and one italic word */
export type HeadlineProps = ClimbComponentProps;
/** Pill buttons with a spring hover, one primary per view, and the pull link */
export type ButtonProps = ClimbComponentProps;
/** Small uppercase labels and the orange rule */
export type EyebrowProps = ClimbComponentProps;
/** Tilted stickers that pin to a card or photo corner */
export type StickerProps = ClimbComponentProps;
/** Outlined tags for formats and topics, and the live label */
export type TagsProps = ClimbComponentProps;
/** Giant outlined numbers for section numbers and big stats */
export type OutlineNumeralsProps = ClimbComponentProps;
/** The glass ticket with stub notches, highlighted and on orange */
export type TicketCardProps = ClimbComponentProps;
/** Ticket offers: the pick, the rest, and a closed release */
export type OfferCardsProps = ClimbComponentProps;
/** Price releases as rising steps: past, now and next */
export type ReleaseLadderProps = ClimbComponentProps;
/** Exhibition stands with an outlined floor plan and stock */
export type StandCardsProps = ClimbComponentProps;
/** The orange band for teams and groups */
export type GroupOfferProps = ClimbComponentProps;
/** Photo cards for the big moments */
export type MomentCardProps = ClimbComponentProps;
/** Photo cards that route each audience to its page */
export type AudienceCardProps = ClimbComponentProps;
/** Testimonials from named, real people */
export type QuoteProps = ClimbComponentProps;
/** A festival poster lineup of names in three sizes */
export type LineupProps = ClimbComponentProps;
/** Brown, Heat and Orange fades over Climb26 photos */
export type PhotoFadeProps = ClimbComponentProps;
/** Full-bleed stage photo with the poster line */
export type HeroProps = ClimbComponentProps;
/** The hero with a glass ticket to pick up */
export type HeroWithTicketProps = ClimbComponentProps;
/** Statement, lead and three moment cards */
export type MomentsProps = ClimbComponentProps;
/** A mosaic of Climb26 photos and two quotes */
export type PhotoWallProps = ClimbComponentProps;
/** Climb Orange band with a Dark Brown ticket */
export type TicketBandProps = ClimbComponentProps;
/** Offers, the release ladder, the group offer and the pull link */
export type TicketsProps = ClimbComponentProps;
/** The release ladder on its own */
export type TicketLadderSectionProps = ClimbComponentProps;
/** Exhibition stands with plans and stock */
export type StandsProps = ClimbComponentProps;
/** Apply to speak, with the poster lineup */
export type SpeakerLineupProps = ClimbComponentProps;
/** Rows of partner logos drifting past */
export type LogoMarqueeProps = ClimbComponentProps;
/** Four audience cards on Charcoal */
export type AudienceChooserProps = ClimbComponentProps;
/** A big photo with a sticker and one line */
export type MomentProps = ClimbComponentProps;
/** Climb Orange close with the last question */
export type CloseProps = ClimbComponentProps;
/** Rising chevrons between two sections */
export type DividerProps = ClimbComponentProps;
/** The right logo for the theme: reversed on dark, full colour on light */
export type LogoProps = ClimbComponentProps;
/** Round icon buttons for socials and contact */
export type SocialIconsProps = ClimbComponentProps;
/** The full signature block: contact, logo and icons, notice, photo banner, legal line */
export type EmailSignatureProps = ClimbComponentProps;
/** Shadows and glows from flat to floating */
export type ElevationProps = ClimbComponentProps;
/** Rise, spring and the marquee drift */
export type MotionProps = ClimbComponentProps;
export interface ClimbUK {
  /** Swap preset classes on [data-climb-theme] elements to match <html data-theme>. */
  applyTheme(root?: ParentNode): void;
  /** Duplicate each logo marquee track so it loops. */
  startMarquees(root?: ParentNode): void;
  /** applyTheme + startMarquees, and follow later theme changes. */
  mount(root?: ParentNode): void;
  Presets: ClimbComponent;
  Headline: ClimbComponent;
  Button: ClimbComponent;
  Eyebrow: ClimbComponent;
  Sticker: ClimbComponent;
  Tags: ClimbComponent;
  OutlineNumerals: ClimbComponent;
  TicketCard: ClimbComponent;
  OfferCards: ClimbComponent;
  ReleaseLadder: ClimbComponent;
  StandCards: ClimbComponent;
  GroupOffer: ClimbComponent;
  MomentCard: ClimbComponent;
  AudienceCard: ClimbComponent;
  Quote: ClimbComponent;
  Lineup: ClimbComponent;
  PhotoFade: ClimbComponent;
  Hero: ClimbComponent;
  HeroWithTicket: ClimbComponent;
  Moments: ClimbComponent;
  PhotoWall: ClimbComponent;
  TicketBand: ClimbComponent;
  Tickets: ClimbComponent;
  TicketLadderSection: ClimbComponent;
  Stands: ClimbComponent;
  SpeakerLineup: ClimbComponent;
  LogoMarquee: ClimbComponent;
  AudienceChooser: ClimbComponent;
  Moment: ClimbComponent;
  Close: ClimbComponent;
  Divider: ClimbComponent;
  Logo: ClimbComponent;
  SocialIcons: ClimbComponent;
  EmailSignature: ClimbComponent;
  Elevation: ClimbComponent;
  Motion: ClimbComponent;
}
declare global { interface Window { ClimbUK: ClimbUK } }
