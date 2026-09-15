/*
 * Les prestations cochees sur une fiche spa, ajoutees au panier avec le spa.
 *
 * Dawn n'envoie qu'un seul article par soumission : son formulaire poste
 * « id » et « quantity », pas de liste. Plutot que de reecrire son
 * gestionnaire, on s'interpose.
 *
 * L'ecoute est posee en phase de CAPTURE, donc avant celle de Dawn. Quand des
 * prestations sont cochees, on arrete l'evenement, on les ajoute, puis on
 * relance la soumission : Dawn ajoute alors le spa en dernier et rend le
 * panier complet. L'inverse — laisser Dawn partir en premier — afficherait un
 * tiroir de panier construit avant l'arrivee des prestations.
 *
 * Sans case cochee, on ne fait rien du tout : le comportement d'origine est
 * intact, et une panne de ce script n'empeche jamais d'acheter un spa.
 */
if (!customElements.get('spa-prestations')) {
  customElements.define(
    'spa-prestations',
    class SpaPrestations extends HTMLElement {
      connectedCallback() {
        this.cases = Array.from(this.querySelectorAll('.spa-prestation__case'));
        this.erreur = this.querySelector('[data-spa-prestations-erreur]');
        this.form = this.closest('form') || document.querySelector('product-form form');

        if (!this.form || this.cases.length === 0) return;

        // Le pack contient les deux autres prestations : les cocher ensemble
        // reviendrait a payer deux fois la meme chose.
        this.cases.forEach((c) => c.addEventListener('change', () => this.appliquerExclusion(c)));

        this.form.addEventListener('submit', this.avantEnvoi.bind(this), true);
      }

      appliquerExclusion(modifiee) {
        if (!modifiee.checked) return;
        const estPack = modifiee.dataset.exclusif === 'pack';
        this.cases.forEach((c) => {
          if (c === modifiee) return;
          const conflit = estPack ? c.dataset.exclusif === 'simple' : c.dataset.exclusif === 'pack';
          if (conflit) c.checked = false;
        });
      }

      get selection() {
        return this.cases
          .filter((c) => c.checked && c.dataset.variantId)
          .map((c) => ({ id: Number(c.dataset.variantId), quantity: 1 }));
      }

      avantEnvoi(evt) {
        // Deuxieme passage : les prestations sont deja au panier, on laisse
        // Dawn ajouter le spa.
        if (this.form.dataset.spaPrestationsFaites === '1') {
          delete this.form.dataset.spaPrestationsFaites;
          return;
        }

        const items = this.selection;
        if (items.length === 0) return;

        evt.preventDefault();
        evt.stopImmediatePropagation();
        this.masquerErreur();

        fetch(`${window.routes.cart_add_url}.js`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({ items }),
        })
          .then((reponse) => reponse.json())
          .then((donnees) => {
            if (donnees.status) throw new Error(donnees.description || donnees.message);
            this.form.dataset.spaPrestationsFaites = '1';
            this.cases.forEach((c) => (c.checked = false));
            this.form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
          })
          .catch((erreur) => {
            // Le spa n'a pas ete ajoute : on le dit, plutot que de laisser
            // croire a une commande passee.
            this.afficherErreur(
              "Les prestations n'ont pas pu être ajoutées. Réessayez, ou appelez-nous au 01 60 77 37 00."
            );
            console.error('spa-prestations', erreur);
          });
      }

      afficherErreur(texte) {
        if (!this.erreur) return;
        this.erreur.textContent = texte;
        this.erreur.hidden = false;
      }

      masquerErreur() {
        if (!this.erreur) return;
        this.erreur.hidden = true;
      }
    }
  );
}
