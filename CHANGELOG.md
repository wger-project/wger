# Changelog for the next release

* Removed the temporary `/api/v2/issue-refresh-token` endpoint. It existed only
  so the mobile app could exchange a permanent DRF token for a JWT refresh
  token. That migration has shipped and the app no longer calls it.
