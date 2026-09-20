"""Icônes SVG inline et feuille de style pour l'identité visuelle de l'app.

Palette et sélecteurs choisis pour un rendu "document technique / plan
d'ingénierie" plutôt que le look par défaut de Streamlit, avec un contraste
WCAG vérifié. Thème fixe et unique (voir .streamlit/config.toml) : ce CSS
ne réagit pas à prefers-color-scheme, car le thème custom de Streamlit ne
le fait pas non plus — le faire côté CSS seul créait des îlots sombres sur
une page qui restait claire. Un vrai mode sombre nécessiterait de suivre
le thème natif "Dark" de Streamlit (sélecteur non confirmé, voir risques).
Les sélecteurs data-testid ciblent la convention st<NomDuComposant> de
Streamlit 1.41 ; certains (uploader, download button, progress) sont
déduits de cette convention plutôt que confirmés sur le DOM réel.
"""

_STROKE = 'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'

# Chaque SVG tient sur une seule ligne, sans espace de tête : st.markdown()
# passe par un rendu markdown avant le HTML, et une ligne indentée de 4+
# espaces est interprétée comme un bloc de code (texte brut), pas du HTML.
ICONS = {
    "document": (
        f'<svg width="18" height="18" viewBox="0 0 24 24" {_STROKE}>'
        '<path d="M6 3h9l5 5v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/>'
        '<path d="M15 3v5h5"/><path d="M8.5 13.5h7M8.5 17h5"/></svg>'
    ),
    "form": (
        f'<svg width="18" height="18" viewBox="0 0 24 24" {_STROKE}>'
        '<rect x="4" y="3" width="16" height="18" rx="1.5"/>'
        '<rect x="7.5" y="7" width="2.5" height="2.5"/><path d="M12.5 8.25h4"/>'
        '<rect x="7.5" y="12" width="2.5" height="2.5"/><path d="M12.5 13.25h4"/>'
        '<rect x="7.5" y="17" width="2.5" height="2.5"/><path d="M12.5 18.25h4"/></svg>'
    ),
    "search": (
        f'<svg width="18" height="18" viewBox="0 0 24 24" {_STROKE}>'
        '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.5-4.5"/></svg>'
    ),
    "extract": (
        f'<svg width="18" height="18" viewBox="0 0 24 24" {_STROKE}>'
        '<rect x="3.5" y="3.5" width="8" height="8" rx="1"/>'
        '<rect x="12.5" y="3.5" width="8" height="8" rx="1"/>'
        '<rect x="3.5" y="12.5" width="8" height="8" rx="1"/>'
        '<rect x="12.5" y="12.5" width="8" height="8" rx="1"/></svg>'
    ),
    "fill": (
        f'<svg width="18" height="18" viewBox="0 0 24 24" {_STROKE}>'
        '<path d="M4 20l1-4.2L15.8 5 19 8.2 8.2 19z"/><path d="M13.3 6.5l4.2 4.2"/></svg>'
    ),
    "download": (
        f'<svg width="18" height="18" viewBox="0 0 24 24" {_STROKE}>'
        '<path d="M12 3v12"/><path d="M7.5 10.5L12 15l4.5-4.5"/>'
        '<path d="M4.5 19.5h15"/></svg>'
    ),
    "check": (
        f'<svg width="16" height="16" viewBox="0 0 24 24" {_STROKE}>'
        '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.8 2.8L16.5 9"/></svg>'
    ),
    "warning": (
        f'<svg width="16" height="16" viewBox="0 0 24 24" {_STROKE}>'
        '<path d="M12 4l9 16H3z"/><path d="M12 10.5v3.5"/><path d="M12 17h.01"/></svg>'
    ),
}


def icon(name: str, tone: str = "accent") -> str:
    """Retourne le HTML d'une icône, prête pour st.markdown(..., unsafe_allow_html=True).

    tone="accent" (défaut, bleu, actions/navigation) ou tone="stamp" (rouge —
    signale, comme un tampon sur un document : un avertissement, ou l'étape
    finale d'un formulaire validé/rempli)."""
    css_class = "ffa-icon" if tone == "accent" else "ffa-icon ffa-icon-stamp"
    return f'<span class="{css_class}">{ICONS[name]}</span>'


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* Palette fixe, alignée sur .streamlit/config.toml : ce thème custom ne
   réagit pas à prefers-color-scheme, donc ce CSS ne doit pas en dépendre
   non plus, sous peine d'îlots sombres sur une page qui reste claire
   (c'est exactement le bug observé : cartes de colonne sombres avec un
   texte d'en-tête resté à la couleur claire du thème natif Streamlit). */
:root {
    --ffa-bg: #F5F6F4;
    --ffa-surface: #FFFFFF;
    --ffa-ink: #16233D;
    --ffa-mist: #6B7280;
    --ffa-accent: #2B5A8C;
    --ffa-stamp: #A63A32;
    --ffa-border: #7A8494;
    --ffa-divider: #D8DBE0;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

[data-testid="stSidebar"] {
    border-right: 1px solid var(--ffa-divider);
}

[data-testid="stColumn"] {
    border: 1px solid var(--ffa-border);
    border-radius: 5px;
    padding: 1.25rem;
    background: var(--ffa-surface);
}

[data-testid="stFileUploader"],
[data-testid="stFileUploaderDropzone"] {
    border-radius: 5px;
}

[data-testid="stBaseButton-primary"] {
    background: var(--ffa-accent);
    border-color: var(--ffa-accent);
    border-radius: 5px;
    font-weight: 500;
}

[data-testid="stBaseButton-secondary"] {
    border-radius: 5px;
    font-weight: 500;
    border-color: var(--ffa-border);
    color: var(--ffa-ink);
}

[data-testid="stExpander"],
[data-testid="stStatusWidget"] {
    border: 1px solid var(--ffa-divider);
    border-radius: 5px;
}

[data-testid="stProgress"] > div > div {
    background-color: var(--ffa-accent);
}

.ffa-icon {
    display: inline-flex;
    vertical-align: middle;
    margin-right: 0.4rem;
    color: var(--ffa-accent);
}
.ffa-icon-stamp {
    color: var(--ffa-stamp);
}

.ffa-mono textarea {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
}

.ffa-step-rail {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin: 1.75rem 0 1.25rem 0;
}
.ffa-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
}
.ffa-step:not(:last-child)::after {
    content: "";
    position: absolute;
    top: 1rem;
    left: 60%;
    width: 80%;
    height: 1.5px;
    background: var(--ffa-divider);
    z-index: 0;
}
.ffa-step.is-complete:not(:last-child)::after {
    background: var(--ffa-accent);
}
.ffa-step-number {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    border: 1.5px solid var(--ffa-border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: var(--ffa-mist);
    background: var(--ffa-surface);
    position: relative;
    z-index: 1;
}
.ffa-step.is-complete .ffa-step-number {
    background: var(--ffa-accent);
    border-color: var(--ffa-accent);
    color: #FFFFFF;
}
.ffa-step.is-active .ffa-step-number {
    border-color: var(--ffa-accent);
    color: var(--ffa-accent);
}
.ffa-step-label {
    font-size: 0.8rem;
    color: var(--ffa-mist);
    margin-top: 0.4rem;
    text-align: center;
}
.ffa-step.is-complete .ffa-step-label,
.ffa-step.is-active .ffa-step-label {
    color: var(--ffa-ink);
}
</style>
"""


def step_rail(step_labels: list, current_index: int) -> str:
    """current_index : index (0-based) de l'étape en cours ; les précédentes sont marquées complètes."""
    items = []
    for i, label in enumerate(step_labels):
        state = "is-complete" if i < current_index else ("is-active" if i == current_index else "")
        number = ICONS["check"] if i < current_index else str(i + 1)
        items.append(
            f'<div class="ffa-step {state}">'
            f'<div class="ffa-step-number">{number}</div>'
            f'<div class="ffa-step-label">{label}</div>'
            f'</div>'
        )
    return f'<div class="ffa-step-rail">{"".join(items)}</div>'
