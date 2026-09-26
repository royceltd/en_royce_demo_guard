### Demo Guard (`royce_demo_guard`)

Protects the shared public demo tenant's login (`demo@royceerp.com`) from being
changed by a visitor and locking out everyone after them.

This app is deliberately isolated from Royce's other apps (`kenyan_accountant`,
`royce_payroll_ke`, `royce_talk`) and is meant to be installed on **the demo
site only**. It carries no logic scoped by site name -- its isolation from
real customer tenants comes from never being on their installed-apps list,
not from a runtime check.

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO
bench --site demo.royceerp.com install-app royce_demo_guard
```

Do not install this app on any other site.

### License

mit
