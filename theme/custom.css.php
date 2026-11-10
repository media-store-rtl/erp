<?php
/**
 * Copyright (c) 2023 Eric Seigne <eric.seigne@cap-rel.fr>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

if (!defined('NOREQUIRESOC')) {
	define('NOREQUIRESOC', '1');
}
//if (! defined('NOREQUIRETRAN')) define('NOREQUIRETRAN','1');	// Not disabled because need to do translations
if (!defined('NOCSRFCHECK')) {
	define('NOCSRFCHECK', 1);
}
if (!defined('NOTOKENRENEWAL')) {
	define('NOTOKENRENEWAL', 1);
}
if (!defined('NOLOGIN')) {
	define('NOLOGIN', 1); // File must be accessed by logon page so without login.
}
if (!defined('NOREQUIREHTML')) {
	define('NOREQUIREHTML', 1);
}
if (!defined('NOREQUIREAJAX')) {
	define('NOREQUIREAJAX', '1');
}

session_cache_limiter('public');

require_once __DIR__.'/../main.inc.php'; // __DIR__ allow this script to be included in custom themes
require_once DOL_DOCUMENT_ROOT.'/core/lib/functions2.lib.php';

// Define css type
top_httphead('text/css');
// Important: Following code is to avoid page request by browser and PHP CPU at each Dolibarr page access.
header('Cache-Control: max-age=10800, public, must-revalidate');


print '/* Here, the content of the common custom CSS defined into Home - Setup - Display - CSS'."*/\n";
print getDolGlobalString('MAIN_IHM_CUSTOM_CSS');


/* Medimo ERP visual refinement - additive, theme-safe overrides */
print <<<'MEDIMO_CSS'
:root {
  --medimo-ink: #172b4d;
  --medimo-muted: #64748b;
  --medimo-line: #e5eaf1;
  --medimo-surface: #ffffff;
  --medimo-canvas: #f5f7fb;
  --medimo-primary: #2563eb;
  --medimo-primary-dark: #1d4ed8;
  --medimo-radius: 12px;
}
html, body {
  background: var(--medimo-canvas);
  color: var(--medimo-ink);
  font-family: Tahoma, "Segoe UI", Arial, sans-serif;
}
#id-top, .tmenu, .tmenu .tmenudiv, .header, .login_table {
  font-family: Tahoma, "Segoe UI", Arial, sans-serif;
}
#id-top {
  box-shadow: 0 2px 14px rgba(20, 39, 70, .08);
}
.tmenu, .tmenu .tmenudiv {
  transition: background-color .18s ease, color .18s ease;
}
.tmenu:hover, .tmenu .tmenudiv:hover {
  filter: brightness(.97);
}
.fiche, .fichecenter, .fichehalfleft, .fichehalfright {
  border-radius: var(--medimo-radius);
}
.box, .info-box, .div-table-responsive, .fichecenter .border, .tabBar {
  border-radius: var(--medimo-radius);
}
.box, .info-box {
  background: var(--medimo-surface);
  border: 1px solid var(--medimo-line);
  box-shadow: 0 4px 18px rgba(25, 45, 75, .045);
}
.box {
  overflow: hidden;
}
.liste_titre, tr.liste_titre th, .fiche .titre {
  color: var(--medimo-ink);
}
table.noborder tr.liste_titre, table.liste tr.liste_titre {
  background: #f1f5f9;
}
table.liste, table.noborder {
  border-color: var(--medimo-line);
}
table.liste td, table.noborder td, table.liste th {
  border-color: var(--medimo-line);
}
table.liste tr.oddeven:hover, table.noborder tr.oddeven:hover {
  background: #f8fbff;
}
input:not([type="checkbox"]):not([type="radio"]):not([type="submit"]),
select, textarea, .select2-container .select2-selection {
  border: 1px solid #d8e0eb;
  border-radius: 8px;
  min-height: 36px;
  transition: border-color .15s ease, box-shadow .15s ease;
}
input:focus, select:focus, textarea:focus,
.select2-container--default.select2-container--focus .select2-selection {
  border-color: #8bb5ff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, .10);
  outline: 0;
}
button, input[type="submit"], .butAction, .button, a.button {
  border-radius: 8px;
  transition: transform .15s ease, box-shadow .15s ease, background-color .15s ease;
}
.butAction, input[type="submit"].butAction {
  box-shadow: 0 3px 9px rgba(37, 99, 235, .14);
}
.butAction:hover, input[type="submit"].butAction:hover {
  transform: translateY(-1px);
  box-shadow: 0 5px 13px rgba(37, 99, 235, .18);
}
.info-box {
  min-height: 94px;
}
.info-box-content {
  padding: 12px 14px;
}
.info-box-title {
  color: var(--medimo-muted);
  font-weight: 600;
}
.info-box-number, .info-box-text {
  color: var(--medimo-ink);
}
.badge, .classfortooltip.badge {
  border-radius: 999px;
  padding: 3px 9px;
}
.tabBar {
  border-bottom: 1px solid var(--medimo-line);
}
.tabactive, .tab {
  border-radius: 8px 8px 0 0;
}
a {
  transition: color .15s ease;
}
a:hover {
  color: var(--medimo-primary-dark);
}
.pagination a, .pagination span {
  border-radius: 7px;
}
@media (max-width: 768px) {
  .fichecenter, .fichecenterbis {
    padding-left: 8px;
    padding-right: 8px;
  }
  .info-box {
    margin-bottom: 10px;
  }
  table.liste {
    font-size: 12px;
  }
}
MEDIMO_CSS;
