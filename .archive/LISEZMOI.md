# Archive des corps de page

Ce dossier conserve le contenu du champ « corps » de trois pages Shopify,
tel qu'il existait le 22 septembre 2026, juste avant d'être vidé.

## Pourquoi ces fichiers existent

Ces trois pages ont reçu une nouvelle mise en page, construite en sections
de thème et non plus dans le corps de la page. Leur gabarit n'appelle donc
plus la section `main-page` : le corps n'était plus affiché, mais restait
visible dans l'administration Shopify, où il invitait à la confusion — on
pouvait le modifier en croyant modifier la page.

Le corps a donc été vidé. Or **Shopify ne conserve aucun historique du
corps d'une page** : une fois vidé, il ne se restaure pas. D'où cette
archive.

| fichier | page | gabarit qui la remplace |
|---|---|---|
| `corps-a-propos.html` | `/pages/a-propos` | `templates/page.a-propos.json` |
| `corps-showroom-spa-essonne.html` | `/pages/showroom-spa-essonne` | `templates/page.showroom.json` |
| `corps-livraison-et-retrait.html` | `/pages/livraison-et-retrait` | `templates/page.livraison.json` |

## Ce qui n'est pas perdu

Tout le **texte** de ces pages vit désormais dans les gabarits ci-dessus,
vérifié phrase par phrase au moment de la reprise : 33 phrases sur 33 pour
« À propos », 25 sur 25 pour le Showroom, 27 sur 27 pour « Livraison et
retrait », et l'intégralité des liens internes.

Ces fichiers ne servent donc qu'à un seul cas : revenir à l'ancienne mise
en page. Il faudrait alors remettre le corps dans la page **et** rétablir
l'ancien gabarit, que l'historique Git conserve.

## Deux valeurs périmées, gardées telles quelles

`corps-a-propos.html` affiche encore « 4,8/5 » et « 18 avis Google ». Le
reste du site dit 4,9/5 et 24 avis depuis. L'archive n'est pas corrigée :
elle doit refléter ce qui existait, pas ce qui aurait dû exister.

## Ce dossier n'est pas envoyé à Shopify

Shopify ne synchronise que `assets`, `blocks`, `config`, `layout`,
`locales`, `sections`, `snippets` et `templates`. Un dossier commençant par
un point est ignoré.
