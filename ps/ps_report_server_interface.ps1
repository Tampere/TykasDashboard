# Asennetaan ensin PowerShellin sisällä tarvittava työkalu
Install-Module -Name ReportingServicesTools

# Loitsutaan pyyntö PowerBI hakemiston /Tampere/TYKAS sisällön tuomiseen
# serveriltä https://TamperePowerBIServer/Reports siten että
# tiedostot tehdään rekursiivisesti (alikansioineen) polkuun C:\temp käyttäjän koneelle
Out-RsRestFolderContent -RsFolder /Tampere/TYKAS -ReportPortalUri 'https://TamperePowerBIServer/Reports' -Destination C:\temp -Recurse