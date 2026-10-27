# Compile Master Transcription File: 1792-1809 - Yogya Residency Letters.md

$sb = [System.Text.StringBuilder]::new()

[void]$sb.AppendLine("# Yogyakarta Residency Letters 1792–1809")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("Transcribed from the Peter Carey Archive")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("## Editorial Note")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("This volume comprises a complete, diplomatic archival transcription of Peter Carey's research notes on the Yogyakarta Residency Letters covering the critical period of 1792–1809. The archive draws from the original collections preserved at the Arsip Nasional Republik Indonesia (ANRI) in Jakarta (Djokjo Brieven series, notably Dj. Br. 22, 23, 24, 25, 41, 45, 49), the Koninklijk Instituut voor Taal-, Land- en Volkenkunde (KITLV, Leiden, MSS H 698a-b, 699), and the British Library (Add MS 12303, Add MS 12341, Raffles-Minto Coll. Eur F. 148/18).")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("The transcription follows strict diplomatic fidelity to the handwritten notes, preserving Dutch and Javanese orthography, diacritical marks, strikethroughs, marginalia, red ink annotations, insertions, and structural headings across all 413 archival photographic folios (comprising the Cover series, Batch 1 [IMG_20260618 series], and Batch 2 [IMG_20260619 series]).")
[void]$sb.AppendLine("")

# Abbreviations table
$abbrText = @"
## Abbreviations

### Rulers and Titles

| Abbreviation | Expansion |
|---|---|
| HB II | Hamengkubuwana II, Sultan of Yogyakarta |
| PB III | Pakubuwana III, Susuhunan of Surakarta |
| PB IV | Pakubuwana IV, Susuhunan of Surakarta |
| MN I | Mangkunegara I (Raden Mas Said, reigned 1757–1795) |
| MN / M.N. | Mangkunagaran (princely house of Surakarta) |
| MB | Mangkubumi (title, often refers to the Sultan) |
| MB II / M.B.II | Hamengkubuwana II |
| P. | Pangéran (prince) |
| R. | Raden (Javanese noble title) |
| R.A. | Raden Ayu (Javanese noble title for women) |
| R.M. | Raden Mas (Javanese noble title) |
| R.T. | Raden Tumenggung (Javanese noble/official title) |
| R.T. / Rg. | Raden Tumenggung / regent (Dutch: regent = bupati) |
| Ng. | Ngabehi (Javanese official title) |
| Kyai | Religious or honorary title |
| S.S. | Susuhunan (title of the Surakarta ruler) |
| CP / C.P. | Crown Prince (Kroonprins) |
| DR I / D.R.I. | Danureja I (the Patih / chief minister of Yogyakarta) |
| DR II | Danureja II |
| PWP / P.W.P. | Pangéran Aria Prabu Prangwedana (later Mangkunegara II) |
| PWD | Pangéran Prangwedana (Col-Commandant of the Legion; Mangkunagara II) |

### Institutions and Geography

| Abbreviation | Expansion |
|---|---|
| V.O.C. | Vereenigde Oost-Indische Compagnie (Dutch East India Company) |
| E.I.C. | East India Company (British) |
| G.G. | Gouverneur-Generaal (Governor-General) |
| N.E. | Java's Northeast Coast (administrative region) |
| N.O.K. | Noordoost Kust (Northeast Coast of Java) |
| A.N. / ANRI | Arsip Nasional (Republik Indonesia) |
| KITLV | Koninklijk Instituut voor Taal-, Land- en Volkenkunde |
| TNI | Tijdschrift voor Nederlandsch-Indië |
| E.MN | Eastern mancanagara (Madiun group) |
| MNI | Mangkunagara I |

### Currency and Units

| Abbreviation | Expansion |
|---|---|
| R.R. | Ronde Reaal / Rixdollar (silver coin) |
| N.D. | Nederlandsche Ducaten (Dutch ducats) |
| Stuiver | Dutch coin (1/20 guilder) |
| Dubbeltje | Dutch 10-cent coin (2 stuivers) |
| Pikul | Unit of weight (approx. 125 lbs / 60 kg) |
| Bau | Traditional Javanese land measurement |
| Jung | Javanese land unit (approx. 4 cacah) |
| Cacah | Javanese land/household tax unit |
| Corge | Unit of count (20 pieces) |

### Officials and Persons

| Abbreviation | Expansion |
|---|---|
| Wat / Waterloo | Waterloo, Resident of Yogyakarta |
| Eng / N.E. | Nicolaas Engelhard, Gov. of Java's NE Coast |
| VdB / V.D.B. | Van den Berg, colonial official |
| Van IJ | Van IJsseldijk, Resident of Yogyakarta |
| D. | Herman Willem Daendels, Gov.-Gen. (1808–1811) |
| W.A. | W.A. Alting, Governor-General |
| G.W. | G.W. (Gustaf Wilhelm) Wiese, Resident of Yogyakarta (1808–09) |
| J.A. | J.A. van Braam, colonial official |
| A.H. | A.H. (Albertus Henricus) Wiese, Governor-General of the Dutch East Indies (1805–1808) |
| A.A. | A.A. Buyskes, Rear-Admiral / Lt-Governor-General |
| B.F. | B.F. von Liebeherr, Resident of Surakarta |
| Van Ovt / P.G. | P.G. van Overstraten, Governor-General |
| J.F.W. van Nes | Commissioner J.F.W. van Nes (1847) |
| Van Pabst | P.H. van Lawick van Pabst, Resident of Rembang (1808–1811) |
| von Winckelmann | F.C.P. von Winckelmann, Brigadier-General, Inspector-General of Forests |
| Raden Rangga | Raden Rangga Prawiradirja III, bupati wedana of Madiun (1796–1810) |
| Sasradiningrat | Surakarta patih (in office 1812–1846) |

### Document References

| Abbreviation | Expansion |
|---|---|
| MvO | Memorie van Overgave (memoir of transfer) |
| AvJ | Archief van Jogja (KITLV H 698a-b, 699) |
| Dj. Br. | Djokjo Brieven series (ANRI) |
| MSS | Manuscripts |
| A.J. | Anno Javanico (Javanese calendar year) |

### Other Terms

| Abbreviation | Expansion |
|---|---|
| Bup. | Bupati (regent) |
| Patih | Chief minister of a Javanese court |
| Pasisir | North coast of Java |
| Kraton | Royal palace/court |
| Sawah | Irrigated rice field |
| Garebeg | Court ceremonial religious festival (Mulud, Puasa, Besar) |
| Puasa | Fasting month (Ramadan) |
| Priyayi | Javanese noble / official class |
| Mantri | Lower-level court or regional official |
| Bekel | Village head / tax collector |
| Wong Durjana | Bandits / robbers / criminals |
| Piagem | Sealed royal charter / decree |
| Pachtgeld | Tax farm rent / revenues |
"@

[void]$sb.AppendLine($abbrText)
[void]$sb.AppendLine("")
[void]$sb.AppendLine("---")
[void]$sb.AppendLine("")

# Cover Files
$coverFiles = @(
    "Cover_IMG_0277.md", "Cover_IMG_0278.md", "Cover_IMG_0279.md", "Cover_IMG_0280.md",
    "Cover_IMG_0281.md", "Cover_IMG_0282.md", "Cover_IMG_0283.md", "Cover_IMG_0284.md"
)

[void]$sb.AppendLine("# Part I: Cover & Archival Index (IMG_0277 – IMG_0284)")
[void]$sb.AppendLine("")

foreach ($f in $coverFiles) {
    $content = Get-Content -Path "transcription/$f" -Raw -Encoding utf8
    [void]$sb.AppendLine($content.Trim())
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("---")
    [void]$sb.AppendLine("")
}

# Batch 1 Files
$batch1Files = Get-ChildItem -Path jpg -Filter "IMG_20260618*.jpg" | Sort-Object Name | ForEach-Object { $_.BaseName + ".md" }

[void]$sb.AppendLine("# Part II: Batch 1 Research Notes (IMG_20260618_0001 – IMG_20260618_0210)")
[void]$sb.AppendLine("")

foreach ($f in $batch1Files) {
    $content = Get-Content -Path "transcription/$f" -Raw -Encoding utf8
    [void]$sb.AppendLine($content.Trim())
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("---")
    [void]$sb.AppendLine("")
}

# Batch 2 Files
$batch2Files = Get-ChildItem -Path jpg -Filter "IMG_20260619*.jpg" | Sort-Object Name | ForEach-Object { $_.BaseName + ".md" }

[void]$sb.AppendLine("# Part III: Batch 2 Research Notes (IMG_20260619_0000 – IMG_20260619_0194)")
[void]$sb.AppendLine("")

foreach ($f in $batch2Files) {
    $content = Get-Content -Path "transcription/$f" -Raw -Encoding utf8
    [void]$sb.AppendLine($content.Trim())
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("---")
    [void]$sb.AppendLine("")
}

$outPath = Join-Path $PSScriptRoot "..\1792-1809 - Yogya Residency Letters.md"
[System.IO.File]::WriteAllText($outPath, $sb.ToString(), [System.Text.Encoding]::UTF8)

$fi = Get-Item $outPath
Write-Host "SUCCESS: 1792-1809 - Yogya Residency Letters.md created: $($fi.Length) bytes, $($sb.ToString().Split("`n").Count) lines"
