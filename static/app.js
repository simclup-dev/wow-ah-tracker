const {
  useState,
  useEffect,
  useCallback,
  useMemo
} = React;
const API = '';
const EXP_LABELS = {
  pandaria: 'Pandaria',
  legion: 'Legion',
  kul_tiran: 'Kul Tiran',
  cataclysm: 'Cataclysm',
  outland: 'Outland',
  draenor: 'Draenor',
  midnight: 'Midnight',
  khaz_algar: 'Khaz Algar'
};
const PROF_LABELS = {
  alchemy: 'Alchemy',
  blacksmithing: 'BS',
  cooking: 'Cooking',
  enchanting: 'Enchanting',
  engineering: 'Engi',
  inscription: 'Inscr',
  jewelcrafting: 'JC',
  leatherworking: 'LW',
  tailoring: 'Tailoring'
};
function fmt(n) {
  if (n == null) return '—';
  return Math.round(n).toLocaleString('en-US');
}
function RealmRow({
  realm
}) {
  const [expanded, setExpanded] = useState(false);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [sortCol, setSortCol] = useState('profit');
  const [sortDir, setSortDir] = useState('desc');
  const toggle = async () => {
    setExpanded(e => !e);
    if (!detail && !loading) {
      setLoading(true);
      try {
        const r = await fetch(`${API}/api/realm/${realm.id}`);
        setDetail(await r.json());
      } catch (e) {}
      setLoading(false);
    }
  };
  const pct = Math.round(realm.passing / realm.total * 100);
  const sortedItems = useMemo(() => {
    if (!detail) return [];
    let items = showAll ? detail.items : detail.items.filter(i => i.passing);
    return [...items].sort((a, b) => {
      let av = a[sortCol],
        bv = b[sortCol];
      if (av == null) av = -Infinity;
      if (bv == null) bv = -Infinity;
      return sortDir === 'desc' ? bv - av : av - bv;
    });
  }, [detail, showAll, sortCol, sortDir]);
  const handleSort = col => {
    if (sortCol === col) setSortDir(d => d === 'desc' ? 'asc' : 'desc');else {
      setSortCol(col);
      setSortDir('desc');
    }
  };
  const arr = col => sortCol === col ? sortDir === 'desc' ? ' ↓' : ' ↑' : '';
  const passingColor = pct > 60 ? 'var(--green)' : pct > 25 ? 'var(--gold)' : 'var(--text-dim)';
  return /*#__PURE__*/React.createElement("div", {
    className: `realm-row${expanded ? ' expanded' : ''}`
  }, /*#__PURE__*/React.createElement("div", {
    className: "realm-header",
    onClick: toggle
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "realm-name"
  }, realm.name), /*#__PURE__*/React.createElement("div", {
    className: "realm-meta",
    style: {
      display: 'flex',
      gap: 8,
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", null, realm.region.toUpperCase()), realm.tier && /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 600,
      fontSize: 11,
      padding: '1px 6px',
      borderRadius: 3,
      background: realm.tier === 'Full' ? '#2e1a00' : realm.tier === 'High' ? '#3d0000' : realm.tier === 'Medium' ? '#3d3000' : realm.tier === 'Low' ? '#0a2e0a' : realm.tier === 'New Players' ? '#0a2a2e' : '#1e2130',
      color: realm.tier === 'Full' ? '#b87333' : realm.tier === 'High' ? '#ff3333' : realm.tier === 'Medium' ? '#d4b84a' : realm.tier === 'Low' ? '#4caf7d' : realm.tier === 'New Players' ? '#4ab8c8' : '#6b7080'
    }
  }, realm.tier), /*#__PURE__*/React.createElement("span", null, "\xB7 ", realm.last_updated ? realm.last_updated.slice(11, 16) + ' UTC' : '—'))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "col-label"
  }, "AH Size"), /*#__PURE__*/React.createElement("div", {
    className: "realm-ah"
  }, fmt(realm.total_auctions))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "col-label"
  }, "Passing"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 16,
      fontWeight: 700,
      color: passingColor
    }
  }, realm.passing, "/", realm.total)), /*#__PURE__*/React.createElement("div", {
    className: "passing-fill"
  }, /*#__PURE__*/React.createElement("div", {
    className: "passing-fill-inner",
    style: {
      width: pct + '%'
    }
  }))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "col-label"
  }, "Est. Profit"), /*#__PURE__*/React.createElement("div", {
    className: "realm-profit"
  }, realm.total_profit > 0 ? fmt(realm.total_profit) + 'g' : '—')), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "col-label"
  }, "Last Update"), /*#__PURE__*/React.createElement("div", {
    className: "realm-meta"
  }, realm.last_updated ? realm.last_updated.slice(5, 16) : '—')), /*#__PURE__*/React.createElement("div", {
    className: `expand-btn${expanded ? ' open' : ''}`
  }, "\u25BC")), expanded && /*#__PURE__*/React.createElement("div", {
    className: "realm-detail fade-in"
  }, /*#__PURE__*/React.createElement("div", {
    className: "detail-controls"
  }, /*#__PURE__*/React.createElement("button", {
    className: `btn toggle-filter${!showAll ? ' active' : ''}`,
    onClick: e => {
      e.stopPropagation();
      setShowAll(false);
    }
  }, "Passing only"), /*#__PURE__*/React.createElement("button", {
    className: `btn toggle-filter${showAll ? ' active' : ''}`,
    onClick: e => {
      e.stopPropagation();
      setShowAll(true);
    }
  }, "All items"), loading && /*#__PURE__*/React.createElement("div", {
    className: "spinner"
  })), detail ? /*#__PURE__*/React.createElement("table", {
    className: "items-table"
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement("th", {
    style: {
      width: 36
    }
  }), /*#__PURE__*/React.createElement("th", null, "Item"), /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'right'
    },
    onClick: () => handleSort('ah_price')
  }, "AH Price", arr('ah_price')), /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'right'
    },
    onClick: () => handleSort('my_min')
  }, "My Min", arr('my_min')), /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'right'
    },
    onClick: () => handleSort('profit')
  }, "Profit", arr('profit')), /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'right'
    },
    onClick: () => handleSort('num_auctions')
  }, "Lots", arr('num_auctions')))), /*#__PURE__*/React.createElement("tbody", null, sortedItems.map(item => /*#__PURE__*/React.createElement("tr", {
    key: item.id,
    className: item.passing ? 'passing' : 'failing'
  }, /*#__PURE__*/React.createElement("td", null, /*#__PURE__*/React.createElement("img", {
    className: "item-icon",
    src: item.icon,
    alt: "",
    onError: e => e.target.style.display = 'none'
  })), /*#__PURE__*/React.createElement("td", null, /*#__PURE__*/React.createElement("div", {
    className: "item-name"
  }, item.name), item.quantity > 1 && /*#__PURE__*/React.createElement("div", {
    className: "item-qty"
  }, "\xD7", item.quantity)), /*#__PURE__*/React.createElement("td", {
    className: `price-cell${item.ah_price ? item.passing ? ' price-pass' : ' price-fail' : ' price-none'}`
  }, item.ah_price ? fmt(item.ah_price) + 'g' : '—'), /*#__PURE__*/React.createElement("td", {
    className: "price-cell"
  }, fmt(item.my_min), "g"), /*#__PURE__*/React.createElement("td", {
    className: `profit-cell${item.profit != null ? item.profit > 0 ? ' profit-pos' : ' profit-neg' : ''}`
  }, item.profit != null ? (item.profit > 0 ? '+' : '') + fmt(item.profit) + 'g' : '—'), /*#__PURE__*/React.createElement("td", {
    className: "auctions-cell"
  }, item.num_auctions || '—'))))) : /*#__PURE__*/React.createElement("div", {
    className: "loading"
  }, /*#__PURE__*/React.createElement("div", {
    className: "spinner"
  }))));
}
function RealmPage({
  region
}) {
  const [realms, setRealms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('total_auctions');
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/realms?region=${region}`);
      setRealms(await r.json());
    } catch (e) {}
    setLoading(false);
  }, [region]);
  useEffect(() => {
    load();
  }, [load]);
  const filtered = useMemo(() => {
    let r = realms.filter(r => r.name.toLowerCase().includes(search.toLowerCase()));
    r.sort((a, b) => {
      if (sortBy === 'total_auctions') return b.total_auctions - a.total_auctions;
      if (sortBy === 'passing') return b.passing - a.passing;
      if (sortBy === 'profit') return b.total_profit - a.total_profit;
      return 0;
    });
    return r;
  }, [realms, search, sortBy]);
  const totalProfit = useMemo(() => filtered.reduce((s, r) => s + r.total_profit, 0), [filtered]);
  const topRealm = useMemo(() => filtered.length ? filtered.reduce((a, b) => b.passing > a.passing ? b : a, filtered[0]) : null, [filtered]);
  const lastUpdate = realms.length ? realms[0].last_updated : null;
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "summary-bar"
  }, /*#__PURE__*/React.createElement("div", {
    className: "stat-card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "stat-label"
  }, "Realms"), /*#__PURE__*/React.createElement("div", {
    className: "stat-value"
  }, filtered.length)), /*#__PURE__*/React.createElement("div", {
    className: "stat-card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "stat-label"
  }, "Total Passing"), /*#__PURE__*/React.createElement("div", {
    className: "stat-value green"
  }, filtered.reduce((s, r) => s + r.passing, 0))), /*#__PURE__*/React.createElement("div", {
    className: "stat-card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "stat-label"
  }, "Est. Total Profit"), /*#__PURE__*/React.createElement("div", {
    className: "stat-value gold"
  }, fmt(totalProfit), "g")), /*#__PURE__*/React.createElement("div", {
    className: "stat-card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "stat-label"
  }, "Best Realm"), /*#__PURE__*/React.createElement("div", {
    className: "stat-value",
    style: {
      fontSize: 16
    }
  }, topRealm ? topRealm.name : '—'))), /*#__PURE__*/React.createElement("div", {
    className: "controls"
  }, /*#__PURE__*/React.createElement("input", {
    className: "search-input",
    placeholder: "Search realm...",
    value: search,
    onChange: e => setSearch(e.target.value)
  }), /*#__PURE__*/React.createElement("select", {
    className: "sort-select",
    value: sortBy,
    onChange: e => setSortBy(e.target.value)
  }, /*#__PURE__*/React.createElement("option", {
    value: "total_auctions"
  }, "Sort: AH Size"), /*#__PURE__*/React.createElement("option", {
    value: "passing"
  }, "Sort: Passing Items"), /*#__PURE__*/React.createElement("option", {
    value: "profit"
  }, "Sort: Est. Profit")), /*#__PURE__*/React.createElement("button", {
    className: "btn",
    onClick: load
  }, "\u21BB Refresh"), lastUpdate && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12,
      color: 'var(--text-dim)',
      fontFamily: 'Share Tech Mono'
    }
  }, lastUpdate.slice(0, 16), " UTC")), loading ? /*#__PURE__*/React.createElement("div", {
    className: "loading"
  }, /*#__PURE__*/React.createElement("div", {
    className: "spinner"
  }), "\xA0Loading...") : /*#__PURE__*/React.createElement("div", {
    className: "realm-list"
  }, filtered.map(r => /*#__PURE__*/React.createElement(RealmRow, {
    key: r.id,
    realm: r
  }))));
}
function DecorRealmRow({
  realm,
  expFilter,
  profFilter
}) {
  const [expanded, setExpanded] = useState(false);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sortCol, setSortCol] = useState('profit');
  const [sortDir, setSortDir] = useState('desc');
  const toggle = async () => {
    setExpanded(e => !e);
    if (!detail && !loading) {
      setLoading(true);
      try {
        const r = await fetch(`${API}/api/decor/realm/${realm.id}`);
        setDetail(await r.json());
      } catch (e) {}
      setLoading(false);
    }
  };
  const handleSort = col => {
    if (sortCol === col) setSortDir(d => d === 'desc' ? 'asc' : 'desc');else {
      setSortCol(col);
      setSortDir('desc');
    }
  };
  const arr = col => sortCol === col ? sortDir === 'desc' ? ' ↓' : ' ↑' : '';
  const filteredItems = useMemo(() => {
    if (!detail) return [];
    let items = detail.items;
    if (expFilter) items = items.filter(i => i.expansion === expFilter);
    if (profFilter) items = items.filter(i => i.profession === profFilter);
    return [...items].sort((a, b) => {
      let av = a[sortCol] ?? -Infinity,
        bv = b[sortCol] ?? -Infinity;
      return sortDir === 'desc' ? bv - av : av - bv;
    });
  }, [detail, expFilter, profFilter, sortCol, sortDir]);
  const profitableColor = realm.profitable > 0 ? 'var(--green)' : 'var(--text-dim)';
  const pct = realm.total > 0 ? Math.round(realm.profitable / realm.total * 100) : 0;
  return /*#__PURE__*/React.createElement("div", {
    className: `realm-row${expanded ? ' expanded' : ''}`
  }, /*#__PURE__*/React.createElement("div", {
    className: "realm-header",
    onClick: toggle
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "realm-name"
  }, realm.name), /*#__PURE__*/React.createElement("div", {
    className: "realm-meta",
    style: {
      display: 'flex',
      gap: 8,
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", null, realm.region.toUpperCase()), realm.tier && /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 600,
      fontSize: 11,
      padding: '1px 6px',
      borderRadius: 3,
      background: realm.tier === 'Full' ? '#2e1a00' : realm.tier === 'High' ? '#3d0000' : realm.tier === 'Medium' ? '#3d3000' : realm.tier === 'Low' ? '#0a2e0a' : '#1e2130',
      color: realm.tier === 'Full' ? '#b87333' : realm.tier === 'High' ? '#ff3333' : realm.tier === 'Medium' ? '#d4b84a' : realm.tier === 'Low' ? '#4caf7d' : '#6b7080'
    }
  }, realm.tier), /*#__PURE__*/React.createElement("span", null, "\xB7 ", realm.last_updated ? realm.last_updated.slice(11, 16) + ' UTC' : '—'))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "col-label"
  }, "AH Size"), /*#__PURE__*/React.createElement("div", {
    className: "realm-ah"
  }, fmt(realm.total_auctions))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "col-label"
  }, "Profitable"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 16,
      fontWeight: 700,
      color: profitableColor
    }
  }, realm.profitable, "/", realm.total), /*#__PURE__*/React.createElement("div", {
    className: "passing-fill"
  }, /*#__PURE__*/React.createElement("div", {
    className: "passing-fill-inner",
    style: {
      width: pct + '%',
      background: 'var(--green)'
    }
  }))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "col-label"
  }, "Est. Profit"), /*#__PURE__*/React.createElement("div", {
    className: "realm-profit"
  }, realm.total_profit > 0 ? fmt(realm.total_profit) + 'g' : '—')), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "col-label"
  }, "Last Update"), /*#__PURE__*/React.createElement("div", {
    className: "realm-meta"
  }, realm.last_updated ? realm.last_updated.slice(5, 16) : '—')), /*#__PURE__*/React.createElement("div", {
    className: `expand-btn${expanded ? ' open' : ''}`
  }, "\u25BC")), expanded && /*#__PURE__*/React.createElement("div", {
    className: "realm-detail fade-in"
  }, loading && /*#__PURE__*/React.createElement("div", {
    className: "loading"
  }, /*#__PURE__*/React.createElement("div", {
    className: "spinner"
  })), detail && /*#__PURE__*/React.createElement("table", {
    className: "items-table"
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement("th", {
    style: {
      width: 32
    }
  }), /*#__PURE__*/React.createElement("th", {
    onClick: () => handleSort('name')
  }, "Item", arr('name')), /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'center',
      width: 90
    }
  }, "Expansion"), /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'center',
      width: 80
    }
  }, "Prof"), /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'right'
    },
    onClick: () => handleSort('ah_price')
  }, "AH Price", arr('ah_price')), /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'right'
    },
    onClick: () => handleSort('cost')
  }, "Cost", arr('cost')), /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'right'
    },
    onClick: () => handleSort('profit')
  }, "Profit", arr('profit')), /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'right'
    },
    onClick: () => handleSort('num_auctions')
  }, "Lots", arr('num_auctions')))), /*#__PURE__*/React.createElement("tbody", null, filteredItems.length === 0 && /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement("td", {
    colSpan: 8,
    style: {
      textAlign: 'center',
      color: 'var(--text-dim)',
      padding: 20
    }
  }, "No items listed")), filteredItems.map(item => /*#__PURE__*/React.createElement("tr", {
    key: item.id
  }, /*#__PURE__*/React.createElement("td", null, /*#__PURE__*/React.createElement("img", {
    className: "item-icon",
    src: item.icon,
    alt: "",
    onError: e => e.target.style.display = 'none'
  })), /*#__PURE__*/React.createElement("td", null, /*#__PURE__*/React.createElement("div", {
    className: "item-name"
  }, item.name)), /*#__PURE__*/React.createElement("td", {
    style: {
      textAlign: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "exp-tag"
  }, EXP_LABELS[item.expansion] || item.expansion)), /*#__PURE__*/React.createElement("td", {
    style: {
      textAlign: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "exp-tag"
  }, PROF_LABELS[item.profession] || item.profession)), /*#__PURE__*/React.createElement("td", {
    className: "price-cell price-pass"
  }, item.ah_price ? fmt(item.ah_price) + 'g' : '—'), /*#__PURE__*/React.createElement("td", {
    className: "price-cell",
    title: !item.cost_known ? 'Не всі ціни реагентів відомі' : ''
  }, item.cost > 0 ? fmt(item.cost) + (item.cost_known ? 'g' : 'g?') : '?'), /*#__PURE__*/React.createElement("td", {
    className: `profit-cell${item.profit != null && item.cost_known ? item.profit > 0 ? ' profit-pos' : ' profit-neg' : ''}`
  }, item.profit != null && item.cost_known ? (item.profit > 0 ? '+' : '') + fmt(item.profit) + 'g' : item.profit != null ? '~' + fmt(item.profit) + 'g?' : '—'), /*#__PURE__*/React.createElement("td", {
    className: "auctions-cell"
  }, item.num_auctions || '—')))))));
}
function DecorPage({
  region
}) {
  const [realms, setRealms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('total_auctions');
  const [expFilter, setExpFilter] = useState('');
  const [profFilter, setProfFilter] = useState('');
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        region
      });
      if (expFilter) params.set('expansion', expFilter);
      if (profFilter) params.set('profession', profFilter);
      const r = await fetch(`${API}/api/decor?${params}`);
      setRealms(await r.json());
    } catch (e) {}
    setLoading(false);
  }, [region, expFilter, profFilter]);
  useEffect(() => {
    load();
  }, [load]);
  const filtered = useMemo(() => {
    let r = realms.filter(r => r.name.toLowerCase().includes(search.toLowerCase()));
    r.sort((a, b) => {
      if (sortBy === 'total_auctions') return b.total_auctions - a.total_auctions;
      if (sortBy === 'profitable') return b.profitable - a.profitable;
      if (sortBy === 'profit') return b.total_profit - a.total_profit;
      return 0;
    });
    return r;
  }, [realms, search, sortBy]);
  const topRealm = useMemo(() => filtered.length ? filtered.reduce((a, b) => b.profitable > a.profitable ? b : a, filtered[0]) : null, [filtered]);
  const lastUpdate = realms.length ? realms[0].last_updated : null;
  const EXPANSIONS = ['pandaria', 'legion', 'kul_tiran', 'cataclysm', 'draenor'];
  const PROFESSIONS = ['alchemy', 'blacksmithing', 'cooking', 'enchanting', 'engineering', 'inscription', 'jewelcrafting', 'leatherworking', 'tailoring'];
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "summary-bar"
  }, /*#__PURE__*/React.createElement("div", {
    className: "stat-card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "stat-label"
  }, "Realms"), /*#__PURE__*/React.createElement("div", {
    className: "stat-value"
  }, filtered.length)), /*#__PURE__*/React.createElement("div", {
    className: "stat-card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "stat-label"
  }, "Total Profitable"), /*#__PURE__*/React.createElement("div", {
    className: "stat-value",
    style: {
      color: 'var(--green)'
    }
  }, filtered.reduce((s, r) => s + r.profitable, 0))), /*#__PURE__*/React.createElement("div", {
    className: "stat-card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "stat-label"
  }, "Est. Total Profit"), /*#__PURE__*/React.createElement("div", {
    className: "stat-value gold"
  }, fmt(filtered.reduce((s, r) => s + r.total_profit, 0)), "g")), /*#__PURE__*/React.createElement("div", {
    className: "stat-card"
  }, /*#__PURE__*/React.createElement("div", {
    className: "stat-label"
  }, "Best Realm"), /*#__PURE__*/React.createElement("div", {
    className: "stat-value",
    style: {
      fontSize: 16
    }
  }, topRealm ? topRealm.name : '—'))), /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: 10
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--text-dim)',
      textTransform: 'uppercase',
      letterSpacing: 1,
      marginBottom: 6
    }
  }, "Expansion"), /*#__PURE__*/React.createElement("div", {
    className: "filter-chips"
  }, /*#__PURE__*/React.createElement("span", {
    className: `chip${!expFilter ? ' active' : ''}`,
    onClick: () => setExpFilter('')
  }, "All"), EXPANSIONS.map(e => /*#__PURE__*/React.createElement("span", {
    key: e,
    className: `chip${expFilter === e ? ' active' : ''}`,
    onClick: () => setExpFilter(f => f === e ? '' : e)
  }, EXP_LABELS[e]))), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--text-dim)',
      textTransform: 'uppercase',
      letterSpacing: 1,
      marginBottom: 6
    }
  }, "Profession"), /*#__PURE__*/React.createElement("div", {
    className: "filter-chips"
  }, /*#__PURE__*/React.createElement("span", {
    className: `chip prof${!profFilter ? ' active' : ''}`,
    onClick: () => setProfFilter('')
  }, "All"), PROFESSIONS.map(p => /*#__PURE__*/React.createElement("span", {
    key: p,
    className: `chip prof${profFilter === p ? ' active' : ''}`,
    onClick: () => setProfFilter(f => f === p ? '' : p)
  }, PROF_LABELS[p])))), /*#__PURE__*/React.createElement("div", {
    className: "controls"
  }, /*#__PURE__*/React.createElement("input", {
    className: "search-input",
    placeholder: "Search realm...",
    value: search,
    onChange: e => setSearch(e.target.value)
  }), /*#__PURE__*/React.createElement("select", {
    className: "sort-select",
    value: sortBy,
    onChange: e => setSortBy(e.target.value)
  }, /*#__PURE__*/React.createElement("option", {
    value: "total_auctions"
  }, "Sort: AH Size"), /*#__PURE__*/React.createElement("option", {
    value: "profitable"
  }, "Sort: Profitable Items"), /*#__PURE__*/React.createElement("option", {
    value: "profit"
  }, "Sort: Est. Profit")), /*#__PURE__*/React.createElement("button", {
    className: "btn",
    onClick: load
  }, "\u21BB Refresh"), lastUpdate && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12,
      color: 'var(--text-dim)',
      fontFamily: 'Share Tech Mono'
    }
  }, lastUpdate.slice(0, 16), " UTC")), loading ? /*#__PURE__*/React.createElement("div", {
    className: "loading"
  }, /*#__PURE__*/React.createElement("div", {
    className: "spinner"
  }), "\xA0Loading...") : /*#__PURE__*/React.createElement("div", {
    className: "realm-list"
  }, filtered.map(r => /*#__PURE__*/React.createElement(DecorRealmRow, {
    key: r.id,
    realm: r,
    expFilter: expFilter,
    profFilter: profFilter
  }))));
}
function SettingsPage({
  sharedData,
  onSaved
}) {
  const {
    recipes: initRecipes,
    allRealms,
    settings: initSettings,
    decorReagentMeta,
    toolsReagentMeta
  } = sharedData;
  const [recipes, setRecipes] = useState(initRecipes);
  const [settings, setSettings] = useState(initSettings);
  const [saved, setSaved] = useState(false);
  const [realmSearch, setRealmSearch] = useState('');
  const [reagentRegion, setReagentRegion] = useState('eu');
  const [decorReagents, setDecorReagents] = useState(initSettings.reagent_prices || {
    eu: {},
    us: {}
  });
  useEffect(() => {
    setRecipes(initRecipes);
  }, [initRecipes]);
  useEffect(() => {
    setSettings(initSettings);
    setDecorReagents(initSettings.reagent_prices || {
      eu: {},
      us: {}
    });
  }, [initSettings]);
  const save = async () => {
    const fullSettings = {
      ...settings,
      reagent_prices: decorReagents
    };
    await fetch(`${API}/api/recipes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(recipes)
    });
    await fetch(`${API}/api/settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(fullSettings)
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    if (onSaved) onSaved(recipes, fullSettings);
  };
  const setDecorReagentPrice = (region, id, val) => setDecorReagents(d => ({
    ...d,
    [region]: {
      ...d[region],
      [id]: parseFloat(val) || 0
    }
  }));
  const updReagent = (key, rank, val) => setRecipes(r => ({
    ...r,
    reagents: {
      ...r.reagents,
      [key]: {
        ...r.reagents[key],
        [rank]: parseFloat(val) || 0
      }
    }
  }));
  const toggleRealm = id => setSettings(s => {
    const h = s.hidden_realms.includes(id) ? s.hidden_realms.filter(x => x !== id) : [...s.hidden_realms, id];
    return {
      ...s,
      hidden_realms: h
    };
  });

  // Іконки для tools reagents по key+rank — ПЕРЕД conditional return
  const toolsIconByKey = useMemo(() => {
    const reg = reagentRegion;
    const m = toolsReagentMeta[reg] || {};
    const out = {};
    Object.values(m).forEach(v => {
      if (!out[v.key]) out[v.key] = {
        icon: v.icon,
        name: v.name,
        rank1_ah: 0,
        rank2_ah: 0
      };
      if (v.rank === 'rank1') out[v.key].rank1_ah = v.price;
      if (v.rank === 'rank2') out[v.key].rank2_ah = v.price;
    });
    return out;
  }, [toolsReagentMeta, reagentRegion]);
  if (!recipes || !initRecipes) return /*#__PURE__*/React.createElement("div", {
    className: "loading"
  }, /*#__PURE__*/React.createElement("div", {
    className: "spinner"
  }));
  const filteredRealms = allRealms.filter(r => r.name.toLowerCase().includes(realmSearch.toLowerCase()));
  const reagentOrder = ['flora', 'mun_ink', 'sie_ink', 'gemdust', 'alloy', 'azeroot', 'lens', 'lotus', 'sun_bolt', 'arc_bolt', 'claw', 'fin', 'hide', 'crystal', 'leather', 'scale'];
  return /*#__PURE__*/React.createElement("div", {
    className: "settings-page"
  }, /*#__PURE__*/React.createElement("div", {
    className: "settings-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "settings-title"
  }, "Reagent Prices"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 14
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      color: 'var(--text-dim)'
    }
  }, "AH \u0446\u0456\u043D\u0438 \u0432 \u0434\u0443\u0436\u043A\u0430\u0445 \u2014 \u0434\u043E\u0432\u0456\u0434\u043A\u043E\u0432\u043E"), /*#__PURE__*/React.createElement("div", {
    className: "region-toggle",
    style: {
      marginBottom: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: `region-btn${reagentRegion === 'eu' ? ' active' : ''}`,
    onClick: () => setReagentRegion('eu')
  }, "EU"), /*#__PURE__*/React.createElement("div", {
    className: `region-btn${reagentRegion === 'us' ? ' active' : ''}`,
    onClick: () => setReagentRegion('us')
  }, "US"))), /*#__PURE__*/React.createElement("div", {
    className: "reagent-grid"
  }, reagentOrder.map(key => {
    const r = recipes.reagents[key];
    if (!r) return null;
    const meta = toolsIconByKey[key];
    return /*#__PURE__*/React.createElement("div", {
      key: key,
      className: "reagent-item"
    }, /*#__PURE__*/React.createElement("div", {
      className: "reagent-label",
      style: {
        display: 'flex',
        alignItems: 'center',
        gap: 5
      }
    }, meta?.icon && /*#__PURE__*/React.createElement("img", {
      src: meta.icon,
      style: {
        width: 16,
        height: 16,
        borderRadius: 2
      },
      alt: "",
      onError: e => e.target.style.display = 'none'
    }), key.replace(/_/g, ' ')), /*#__PURE__*/React.createElement("div", {
      className: "reagent-inputs"
    }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("input", {
      className: "reagent-input",
      type: "number",
      value: r.rank1 || 0,
      onChange: e => updReagent(key, 'rank1', e.target.value),
      title: meta?.rank1_ah ? `AH: ${meta.rank1_ah}g` : ''
    }), /*#__PURE__*/React.createElement("div", {
      className: "reagent-rank"
    }, "rank 1", meta?.rank1_ah > 0 ? ` (${meta.rank1_ah}g)` : '')), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("input", {
      className: "reagent-input",
      type: "number",
      value: r.rank2 || 0,
      onChange: e => updReagent(key, 'rank2', e.target.value),
      title: meta?.rank2_ah ? `AH: ${meta.rank2_ah}g` : ''
    }), /*#__PURE__*/React.createElement("div", {
      className: "reagent-rank"
    }, "rank 2", meta?.rank2_ah > 0 ? ` (${meta.rank2_ah}g)` : ''))));
  }))), /*#__PURE__*/React.createElement("div", {
    className: "settings-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "settings-title"
  }, "Profit & Alerts"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-dim)',
      fontSize: 14
    }
  }, "Min profit margin (gold)"), /*#__PURE__*/React.createElement("input", {
    className: "reagent-input",
    type: "number",
    value: settings.profit_margin != null ? settings.profit_margin : 1000,
    onChange: e => setSettings(s => ({
      ...s,
      profit_margin: parseInt(e.target.value) || 0
    })),
    style: {
      width: 80
    }
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-dim)',
      fontSize: 14
    }
  }, "Alert when passing items change by \xB1"), /*#__PURE__*/React.createElement("input", {
    className: "reagent-input",
    type: "number",
    value: settings.alert_threshold || 5,
    onChange: e => setSettings(s => ({
      ...s,
      alert_threshold: parseInt(e.target.value) || 1
    })),
    style: {
      width: 60
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-dim)',
      fontSize: 14
    }
  }, "items")))), /*#__PURE__*/React.createElement("div", {
    className: "settings-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "settings-title"
  }, "Decor Reagent Prices"), /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: 12,
      fontSize: 13,
      color: 'var(--text-dim)'
    }
  }, "\u0426\u0456\u043D\u0438 \u0437 \u0410\u0413 \u043E\u043D\u043E\u0432\u043B\u044E\u044E\u0442\u044C\u0441\u044F \u0430\u0432\u0442\u043E\u043C\u0430\u0442\u0438\u0447\u043D\u043E. \u041C\u043E\u0436\u043D\u0430 \u043F\u0435\u0440\u0435\u0432\u0438\u0437\u043D\u0430\u0447\u0438\u0442\u0438 \u0432\u0440\u0443\u0447\u043D\u0443."), /*#__PURE__*/React.createElement("div", {
    className: "region-toggle"
  }, /*#__PURE__*/React.createElement("div", {
    className: `region-btn${reagentRegion === 'eu' ? ' active' : ''}`,
    onClick: () => setReagentRegion('eu')
  }, "EU"), /*#__PURE__*/React.createElement("div", {
    className: `region-btn${reagentRegion === 'us' ? ' active' : ''}`,
    onClick: () => setReagentRegion('us')
  }, "US")), /*#__PURE__*/React.createElement("div", {
    className: "reagent-decor-grid"
  }, decorReagentMeta.map(r => {
    const ahPrice = reagentRegion === 'eu' ? r.eu_price : r.us_price;
    const override = decorReagents[reagentRegion]?.[r.id];
    const displayPrice = override != null ? override : ahPrice;
    return /*#__PURE__*/React.createElement("div", {
      key: r.id,
      className: "reagent-decor-item"
    }, r.icon ? /*#__PURE__*/React.createElement("img", {
      className: "reagent-decor-icon",
      src: r.icon,
      alt: "",
      onError: e => e.target.style.display = 'none'
    }) : /*#__PURE__*/React.createElement("div", {
      style: {
        width: 22,
        height: 22,
        background: 'var(--bg0)',
        borderRadius: 3,
        flexShrink: 0
      }
    }), /*#__PURE__*/React.createElement("span", {
      className: "reagent-decor-name",
      title: r.name
    }, r.name), r.is_lumber ? /*#__PURE__*/React.createElement("span", {
      className: "lumber-tag"
    }, "\uD83E\uDEB5 200g") : /*#__PURE__*/React.createElement("input", {
      className: "reagent-decor-input",
      type: "number",
      value: override != null ? override : ahPrice,
      placeholder: ahPrice || '0',
      onChange: e => setDecorReagentPrice(reagentRegion, r.id, e.target.value),
      title: `AH: ${ahPrice}g`
    }));
  }))), /*#__PURE__*/React.createElement("div", {
    className: "settings-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "settings-title"
  }, "Realm Visibility"), /*#__PURE__*/React.createElement("input", {
    className: "search-input",
    placeholder: "Search realm...",
    value: realmSearch,
    onChange: e => setRealmSearch(e.target.value),
    style: {
      marginBottom: 12,
      width: '100%'
    }
  }), /*#__PURE__*/React.createElement("div", {
    className: "realm-settings-list"
  }, filteredRealms.map(realm => {
    const hidden = settings.hidden_realms.includes(realm.id);
    return /*#__PURE__*/React.createElement("div", {
      key: realm.id,
      className: "realm-toggle-item"
    }, /*#__PURE__*/React.createElement("span", {
      className: "realm-toggle-name"
    }, realm.name), /*#__PURE__*/React.createElement("span", {
      className: "realm-toggle-meta"
    }, realm.region.toUpperCase(), " \xB7 ", fmt(realm.total_auctions)), /*#__PURE__*/React.createElement("div", {
      className: `toggle-sw${!hidden ? ' on' : ''}`,
      onClick: () => toggleRealm(realm.id)
    }));
  }))), /*#__PURE__*/React.createElement("button", {
    className: "save-btn",
    onClick: save
  }, saved ? '✓ Saved' : 'Save All Settings'));
}
const PRICE_GROUPS = [{
  label: 'BS',
  items: [{
    id: 237951,
    name: 'bs lw tool set'
  }, {
    id: 237950,
    name: 'bs needlet set'
  }, {
    id: 237952,
    name: 'bs toolbox'
  }, {
    id: 238018,
    name: 'bs tool ×4'
  }]
}, {
  label: 'ENGI',
  items: [{
    id: 244720,
    name: 'engi big'
  }, {
    id: 244714,
    name: 'engi clampers'
  }, {
    id: 244712,
    name: 'engi fish rod'
  }, {
    id: 244716,
    name: 'engi hardhat'
  }, {
    id: 244710,
    name: 'engi headlamp'
  }, {
    id: 244708,
    name: 'engi tailor snippers'
  }]
}, {
  label: 'INSCR',
  items: [{
    id: 245778,
    name: 'inscr alch rod'
  }, {
    id: 245780,
    name: 'inscr cook pin'
  }, {
    id: 245776,
    name: 'inscr quill'
  }]
}, {
  label: 'JC',
  items: [{
    id: 240960,
    name: 'jc crystal'
  }, {
    id: 240958,
    name: 'jc glass'
  }, {
    id: 240959,
    name: 'jc loupes'
  }, {
    id: 240957,
    name: 'jc spec'
  }]
}, {
  label: 'LW',
  items: [{
    id: 244624,
    name: 'lw acces ×2'
  }, {
    id: 244628,
    name: 'lw bs cover'
  }, {
    id: 244621,
    name: 'lw herb back'
  }, {
    id: 244623,
    name: 'lw hunter ×3'
  }, {
    id: 244630,
    name: 'lw jc cover'
  }]
}, {
  label: 'TAILOR',
  items: [{
    id: 239635,
    name: 'tailor arc ×3'
  }, {
    id: 239636,
    name: 'tailor sun ×3'
  }]
}];
function PricesPage() {
  const [region, setRegion] = useState('eu');
  const [prices, setPrices] = useState({});
  const [copied, setCopied] = useState(false);
  useEffect(() => {
    setPrices({});
    fetch(`${API}/api/min_prices?region=${region}`).then(r => r.json()).then(data => {
      setPrices(data);
    });
  }, [region]);
  const copyAll = () => {
    const lines = [];
    PRICE_GROUPS.forEach(g => {
      lines.push('--- ' + g.label + ' ---');
      g.items.forEach(item => {
        const p = prices[item.id];
        lines.push(`${item.name.padEnd(22)} ${p ? fmt(p) + 'g' : '—'}`);
      });
      lines.push('');
    });
    navigator.clipboard.writeText(lines.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  const half = Math.ceil(PRICE_GROUPS.length / 2);
  const col1 = PRICE_GROUPS.slice(0, half);
  const col2 = PRICE_GROUPS.slice(half);
  const renderGroup = group => /*#__PURE__*/React.createElement("div", {
    key: group.label,
    style: {
      marginBottom: 20
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      fontWeight: 700,
      color: 'var(--text-dim)',
      textTransform: 'uppercase',
      letterSpacing: 2,
      marginBottom: 8,
      paddingBottom: 4,
      borderBottom: '1px solid var(--border)'
    }
  }, group.label), group.items.map(item => /*#__PURE__*/React.createElement("div", {
    key: item.id,
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '5px 8px',
      borderRadius: 4,
      cursor: 'pointer',
      transition: 'background .1s'
    },
    onMouseEnter: e => e.currentTarget.style.background = 'var(--bg3)',
    onMouseLeave: e => e.currentTarget.style.background = 'transparent',
    onClick: () => navigator.clipboard.writeText(String(prices[item.id] || ''))
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 14,
      color: 'var(--text)'
    }
  }, item.name), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 14,
      fontFamily: 'Share Tech Mono',
      fontWeight: 600,
      color: prices[item.id] ? 'var(--gold)' : 'var(--text-dim)'
    }
  }, prices[item.id] ? fmt(prices[item.id]) + 'g' : '—'))));
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 20
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 16,
      fontWeight: 700,
      color: 'var(--gold)',
      textTransform: 'uppercase',
      letterSpacing: 1
    }
  }, "Min Prices"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 4
    }
  }, ['eu', 'us'].map(r => /*#__PURE__*/React.createElement("button", {
    key: r,
    className: "btn",
    onClick: () => setRegion(r),
    style: {
      opacity: region === r ? 1 : 0.45,
      fontWeight: region === r ? 700 : 400
    }
  }, r.toUpperCase())))), /*#__PURE__*/React.createElement("button", {
    className: "btn",
    onClick: copyAll
  }, copied ? '✓ Copied' : 'Copy All')), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 32
    }
  }, /*#__PURE__*/React.createElement("div", null, col1.map(renderGroup)), /*#__PURE__*/React.createElement("div", null, col2.map(renderGroup))));
}
function App() {
  const [tab, setTab] = useState('eu');
  const [sharedData, setSharedData] = useState({
    recipes: null,
    allRealms: [],
    settings: {
      hidden_realms: [],
      alert_threshold: 5
    },
    decorReagentMeta: [],
    toolsReagentMeta: {
      eu: {},
      us: {}
    }
  });
  useEffect(() => {
    fetch(`${API}/api/recipes`).then(r => r.json()).then(recipes => setSharedData(d => ({
      ...d,
      recipes
    })));
    fetch(`${API}/api/realms/all`).then(r => r.json()).then(allRealms => setSharedData(d => ({
      ...d,
      allRealms
    })));
    fetch(`${API}/api/settings`).then(r => r.json()).then(settings => setSharedData(d => ({
      ...d,
      settings
    })));
    Promise.all([fetch(`${API}/api/reagent_prices?region=eu`).then(r => r.json()).catch(() => ({})), fetch(`${API}/api/reagent_prices?region=us`).then(r => r.json()).catch(() => ({}))]).then(([eu, us]) => {
      const meta = Object.entries(eu).map(([id, v]) => ({
        id: parseInt(id),
        name: v.name,
        icon: v.icon,
        is_lumber: v.is_lumber,
        eu_price: v.price,
        us_price: (us[id] || {}).price || 0
      }));
      meta.sort((a, b) => a.name.localeCompare(b.name));
      setSharedData(d => ({
        ...d,
        decorReagentMeta: meta
      }));
    });
    Promise.all([fetch(`${API}/api/tools_reagent_prices?region=eu`).then(r => r.json()).catch(() => ({})), fetch(`${API}/api/tools_reagent_prices?region=us`).then(r => r.json()).catch(() => ({}))]).then(([eu, us]) => setSharedData(d => ({
      ...d,
      toolsReagentMeta: {
        eu,
        us
      }
    })));
  }, []);
  const handleSettingsSaved = (recipes, settings) => setSharedData(d => ({
    ...d,
    recipes,
    settings
  }));
  const isDecor = tab === 'eu-decor' || tab === 'us-decor';
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "header"
  }, /*#__PURE__*/React.createElement("div", {
    className: "header-title"
  }, "\u2692 AH Tracker"), /*#__PURE__*/React.createElement("div", {
    className: "header-sub"
  }, isDecor ? 'Midnight · Decor' : 'Midnight · Prof Tools'), /*#__PURE__*/React.createElement("div", {
    className: "header-right"
  }, /*#__PURE__*/React.createElement("div", {
    className: "nav-tabs"
  }, /*#__PURE__*/React.createElement("div", {
    className: `nav-tab${tab === 'eu' ? ' active' : ''}`,
    onClick: () => setTab('eu')
  }, "EU"), /*#__PURE__*/React.createElement("div", {
    className: `nav-tab${tab === 'us' ? ' active' : ''}`,
    onClick: () => setTab('us')
  }, "US"), /*#__PURE__*/React.createElement("div", {
    className: `nav-tab${tab === 'eu-decor' ? ' active' : ''}`,
    onClick: () => setTab('eu-decor'),
    style: {
      color: tab === 'eu-decor' ? 'var(--text-bright)' : 'var(--blue)',
      opacity: tab === 'eu-decor' ? 1 : .7
    }
  }, "EU Decor"), /*#__PURE__*/React.createElement("div", {
    className: `nav-tab${tab === 'us-decor' ? ' active' : ''}`,
    onClick: () => setTab('us-decor'),
    style: {
      color: tab === 'us-decor' ? 'var(--text-bright)' : 'var(--blue)',
      opacity: tab === 'us-decor' ? 1 : .7
    }
  }, "US Decor"), /*#__PURE__*/React.createElement("div", {
    className: `nav-tab${tab === 'prices' ? ' active' : ''}`,
    onClick: () => setTab('prices')
  }, "Prices"), /*#__PURE__*/React.createElement("div", {
    className: `nav-tab${tab === 'settings' ? ' active' : ''}`,
    onClick: () => setTab('settings')
  }, "\u2699 Settings")))), /*#__PURE__*/React.createElement("div", {
    className: "main"
  }, tab === 'eu' && /*#__PURE__*/React.createElement(RealmPage, {
    key: "eu",
    region: "eu"
  }), tab === 'us' && /*#__PURE__*/React.createElement(RealmPage, {
    key: "us",
    region: "us"
  }), tab === 'eu-decor' && /*#__PURE__*/React.createElement(DecorPage, {
    key: "eu-decor",
    region: "eu"
  }), tab === 'us-decor' && /*#__PURE__*/React.createElement(DecorPage, {
    key: "us-decor",
    region: "us"
  }), tab === 'prices' && /*#__PURE__*/React.createElement(PricesPage, null), tab === 'settings' && /*#__PURE__*/React.createElement(SettingsPage, {
    sharedData: sharedData,
    onSaved: handleSettingsSaved
  })));
}
ReactDOM.createRoot(document.getElementById('root')).render(/*#__PURE__*/React.createElement(App, null));

