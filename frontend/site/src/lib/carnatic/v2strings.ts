/* The v2 pages' chrome in Tamil, from the design's own Tamil strings
 * (design/handoff-v2: Course, Lesson Reader, Listening Room and Practice
 * Hub canvases), keyed by the English each page passes as its default.
 * The design gives Tamil only; Telugu and Kannada fall back to the English
 * until those strings are written, and the school's strip already marks
 * the Indic chrome as awaiting a native reader.
 *
 *   const say = localize(lang, await copy("carnatic/learn"));
 *
 * English stays editable in the admin as before (copy()); a Tamil string
 * here wins only when the page is in Tamil.
 */
import type { Copy } from "../copy";
import type { Lang } from "./i18n";

export const TA: Record<string, string> = {
  // the course home, units, glossary
  "The course": "பாடத்திட்டம்",
  "From Sa to ragam tanam pallavi": "ஸ முதல் ராகம் தானம் பல்லவி வரை",
  "{u} units and {l} lessons of Carnatic theory, for any voice or instrument. Levels are labels, not locks: open anything.": "கர்நாடக இசைக் கோட்பாட்டின் {u} அலகுகள், {l} பாடங்கள். நிலைகள் பெயர்கள் மட்டுமே; எதையும் திறக்கலாம்.",
  "Start here": "இங்கே தொடங்கு",
  "Continue": "தொடர்க",
  "The beginner path": "தொடக்கப் பாதை",
  "50 exercises and 4 varnams": "50 பயிற்சிகள், 4 வர்ணங்கள்",
  "The traditional practice order. It runs alongside these units:": "மரபுவழிப் பயிற்சி வரிசை. இந்த அலகுகளுடன் இணைகிறது:",
  "Your progress is kept on this device.": "உங்கள் முன்னேற்றம் இந்தச் சாதனத்தில் சேமிக்கப்படுகிறது.",
  "Sign in to keep it across devices.": "எல்லாச் சாதனங்களிலும் வைத்திருக்க உள்நுழையுங்கள்.",
  "Search lessons, ragas, talas": "பாடங்கள், ராகங்கள், தாளங்களைத் தேடு",
  "Level": "நிலை",
  "All": "எல்லாம்",
  "Foundations": "அடிப்படை",
  "Intermediate": "இடைநிலை",
  "Advanced": "மேல்நிலை",
  "Has listening": "கேட்டல் உண்டு",
  "has listening": "கேட்டல் உண்டு",
  "Has practice piece": "பயிற்சிப் படைப்பு உண்டு",
  "not opened yet": "இன்னும் திறக்கவில்லை",
  "Opened": "திறக்கப்பட்டது",
  "Completed ✓": "முடிந்தது ✓",
  "{o} opened · {c} completed": "{o} திறக்கப்பட்டது · {c} முடிந்தது",
  "Unit": "அலகு",
  "Unit {n}": "அலகு {n}",
  "Lesson {n}": "பாடம் {n}",
  "{n} lessons": "{n} பாடங்கள்",
  "about {d}": "சுமார் {d}",
  "Unit {u} · Lesson {n} · {min} min": "அலகு {u} · பாடம் {n} · {min} நிமி",
  "Unit {u} · Lesson {n} · {min} min left": "அலகு {u} · பாடம் {n} · {min} நிமி மீதம்",
  "{n} lessons match": "{n} பாடங்கள் பொருந்துகின்றன",
  "Glossary": "சொற்களஞ்சியம்",
  "Learn · {n} terms": "கற்க · {n} சொற்கள்",
  "Every term the course uses, with a one-line definition and the lesson that teaches it. In lessons, terms with a dotted underline open the same definition.": "பாடத்திட்டம் பயன்படுத்தும் ஒவ்வொரு சொல்லும்.",
  "You might read": "முதலில்",
  "first.": "படிக்கலாம்.",
  "Unit {n} checkpoint": "அலகு {n} சோதனைப் புள்ளி",
  "10–15 minutes · a profile in words for each skill, not a score": "10–15 நிமிடம் · மதிப்பெண் அல்ல, சொற்களில் விவரம்",
  "Start": "தொடங்கு",
  "Recordings this unit leans on": "இந்த அலகு சார்ந்திருக்கும் பதிவுகள்",
  "Listening room": "கேட்கும் அறை",
  "Learn": "கற்க",
  // the reader
  "On this page": "இந்தப் பக்கத்தில்",
  "Your place is remembered on this device.": "நீங்கள் படித்த இடம் இந்தச் சாதனத்தில் நினைவில் இருக்கும்.",
  "By the end of this lesson you can": "இந்தப் பாடத்தின் முடிவில் உங்களால்",
  "This lesson isn't in {lang} yet. You're reading the English.": "இந்தப் பாடம் இன்னும் தமிழில் இல்லை; ஆங்கிலத்தில் காட்டப்படுகிறது.",
  "Unit {u} · Lesson {n} · {level} · {min} min": "அலகு {u} · பாடம் {n} · {level} · {min} நிமி",
  "Recommended recordings": "பரிந்துரைக்கப்பட்ட பதிவுகள்",
  "Test yourself on this lesson": "இந்தப் பாடத்தில் சோதியுங்கள்",
  "Mark as complete": "முடிந்ததாகக் குறி",
  "You decide when a lesson is complete. Nothing is marked for you.": "பாடம் எப்போது முடிந்தது என்பதை நீங்களே முடிவு செய்கிறீர்கள்.",
  "Next lesson": "அடுத்த பாடம்",
  "Sources": "ஆதாரங்கள்",
  "Lesson {n} · {min} min": "பாடம் {n} · {min} நிமி",
  "What to listen for": "எதைக் கேட்க வேண்டும்",
  "Some schools": "சில பாணிகள்",
  "Sources differ": "ஆதாரங்கள் வேறுபடுகின்றன",
  "Footnote": "அடிக்குறிப்பு",
  "Beginner": "அடிப்படை",
  // practice
  "Test yourself": "சோதியுங்கள்",
  "Ear training": "செவிப் பயிற்சி",
  "Skill map": "திறன் வரைபடம்",
  "Tuner": "சுருதி அளவி",
  "Tala trainer": "தாளப் பயிற்சி",
  "Ready to review": "மீள்பார்வைக்குத் தயார்",
  "Quiz items and drill items share one review queue.": "வினாக்களும் பயிற்சிகளும் ஒரே வரிசையில்.",
  "Mixed review": "கலப்பு மீள்பார்வை",
  "A little of everything you've opened": "நீங்கள் திறந்த எல்லாவற்றிலிருந்தும் சிறிது",
  "Items come from lessons you've read. Retake any time.": "எப்போது வேண்டுமானாலும் மீண்டும் செய்யலாம்.",
  "Topic review": "தலைப்பு மீள்பார்வை",
  "Little quizzes": "சிறு வினாடிவினாக்கள்",
  "Tala keeping": "தாளம் காத்தல்",
  "Unit checkpoints": "அலகுச் சோதனைகள்",
  "Eight drill families, each a ladder of levels. A level opens when you finish the lesson that teaches it; the others show which lesson that is. You can open them anyway.": "எட்டு பயிற்சிக் குடும்பங்கள், ஒவ்வொன்றும் நிலைகளின் ஏணி. ஒரு நிலை அதைக் கற்பிக்கும் பாடத்தை முடித்ததும் திறக்கும்.",
  "For each family, the highest level you're comfortable with, in words.": "ஒவ்வொரு குடும்பத்திலும் நீங்கள் வசதியாக இருக்கும் உயர்ந்த நிலை.",
  "No overall score, by design.": "மொத்த மதிப்பெண் இல்லை.",
  "Your practice": "உங்கள் பயிற்சி",
  "This week": "இந்த வாரம்",
  "Suggested next": "அடுத்து பரிந்துரை",
  "Personal bests": "சிறந்த சாதனைகள்",
  "Feedback on your pieces": "உங்கள் படைப்புகளுக்குக் கருத்து",
  // listening
  "Reference recordings": "குறிப்புப் பதிவுகள்",
  "Guess the raga": "ராகத்தைக் கணியுங்கள்",
  "Hear a recording before you know what it is": "என்ன ராகம் என்று தெரியும் முன் கேளுங்கள்",
  "The raga is hidden until you commit a guess. Analyses stay hidden until then too.": "நீங்கள் கணிக்கும் வரை ராகம் மறைக்கப்பட்டிருக்கும்.",
  "Try one": "முயன்று பாருங்கள்",
  "Analyses": "பகுப்பாய்வுகள்",
  "Newest": "புதியவை",
  "Most discussed": "அதிகம் விவாதிக்கப்பட்டவை",
  "Write an analysis": "பகுப்பாய்வு எழுது",
  "Analyses of recordings you haven't guessed yet are hidden in guess mode, so the discussion can't spoil them.": "நீங்கள் இன்னும் கணிக்காத பதிவுகளின் பகுப்பாய்வுகள் மறைக்கப்பட்டுள்ளன.",
  "Suggest a recording": "ஒரு பதிவைப் பரிந்துரை",
  "Link": "இணைப்பு",
  "Raga": "ராகம்",
  "Composition": "உருப்படி",
  "Why this one": "ஏன் இது",
  "Send suggestion": "அனுப்பு",
  "Your suggestions": "உங்கள் பரிந்துரைகள்",
  "Overview": "கண்ணோட்டம்",
  "Phrases": "பிரயோகங்கள்",
  "Compositions": "உருப்படிகள்",
  "Listening": "கேட்டல்",
  "Lessons": "பாடங்கள்",
};

/** A page's copy in the visitor's language: the design's Tamil where it exists, else the English (editable). */
export function localize(lang: Lang, say: Copy): Copy {
  if (lang !== "ta") return say;
  return (key: string, fallback: string, label?: string) => TA[fallback] ?? say(key, fallback, label);
}
