/*
 * Naukri profile scorer: JavaScript port of naukri_optimizer/core.py.
 * Works in the browser (window.NaukriScorer) and in Node (require).
 * tests/test_parity.py checks it returns exactly what the Python version does.
 * MIT licence. https://github.com/FirstDay-AI/naukri-profile-optimizer
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.NaukriScorer = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var FLUFF = [
    "hardworking", "hard working", "hard-working", "seeking a challenging",
    "challenging position", "challenging role", "dynamic organization",
    "dynamic organisation", "team player", "self motivated", "self-motivated",
    "looking for an opportunity", "looking for a job", "result oriented",
    "result-oriented", "go-getter", "quick learner", "passionate", "dedicated"
  ];

  var GENERIC = [
    "communication", "communication skills", "teamwork", "team work",
    "leadership", "ms office", "microsoft office", "time management",
    "hard working", "hardworking", "problem solving", "interpersonal skills",
    "english", "typing", "internet", "multitasking", "team player"
  ];

  function norm(text) {
    var t = String(text || "").toLowerCase();
    t = t.replace(/[^a-z0-9+#.]+/g, " ");
    t = t.replace(/\.(?=\s|$)/g, " ");
    return " " + t.replace(/\s+/g, " ").trim() + " ";
  }
  function parts(kw) { return kw.split("|").map(function (p) { return p.trim(); }).filter(Boolean); }
  function display(kw) { return parts(kw)[0]; }
  function hasKw(n, kw) { return parts(kw).some(function (p) { return n.indexOf(norm(p)) !== -1; }); }
  function roundHalfUp(x) { return Math.floor(x + 0.5); }
  function isGeneric(s) { return GENERIC.indexOf(s.toLowerCase()) !== -1; }

  function asList(value) {
    if (value === null || value === undefined) return [];
    var items = Array.isArray(value) ? value : String(value).split(/[,\n;|]/);
    var out = [], seen = {};
    items.forEach(function (item) {
      var s = String(item).trim();
      if (s && !seen[s.toLowerCase()]) { seen[s.toLowerCase()] = true; out.push(s); }
    });
    return out;
  }

  function num(v) {
    if (v === null || v === undefined || v === "") return null;
    var n = Number(v);
    return isNaN(n) ? null : n;
  }

  function findRole(profile, roles) {
    var target = String(profile.target_role || "").trim();
    var i, r;
    if (target) {
      for (i = 0; i < roles.length; i++) {
        r = roles[i];
        if (target.toLowerCase() === r.id || target.toLowerCase() === r.name.toLowerCase()) return r;
      }
      var t = norm(target);
      for (i = 0; i < roles.length; i++) {
        r = roles[i];
        if (r.titles.some(function (title) { return t.indexOf(norm(title)) !== -1 || norm(title).indexOf(t.trim()) !== -1; })) return r;
      }
    }
    var probe = norm([profile.headline || "", profile.current_designation || ""].join(" "));
    for (i = 0; i < roles.length; i++) {
      r = roles[i];
      if (r.titles.some(function (title) { return probe.indexOf(norm(title)) !== -1; })) return r;
    }
    return null;
  }

  function analyze(profile, roles) {
    var role = findRole(profile, roles);
    if (!role) {
      throw new Error("Could not tell the target role. Set target_role to one of: " +
        roles.map(function (r) { return r.id; }).join(", "));
    }
    var hname = role.headline_name || role.name;
    var headline = profile.headline || "";
    var summary = profile.summary || "";
    var designation = profile.current_designation || "";
    var skills = asList(profile.key_skills);
    var locations = asList(profile.preferred_locations);
    var years = num(profile.years_experience);
    var updated = num(profile.last_updated_days);
    var notice = num(profile.notice_period_days);

    var nHead = norm(headline), nSum = norm(summary), nDes = norm(designation);
    var nSkills = norm(skills.join(" , "));
    var allKw = role.core.concat(role.extra);
    function isTitle(nt) { return role.titles.some(function (t) { return nt.indexOf(norm(t)) !== -1; }); }
    function count(n) { return allKw.filter(function (k) { return hasKw(n, k); }).length; }
    function fluffIn(text) { var l = text.toLowerCase(); return FLUFF.filter(function (p) { return l.indexOf(p) !== -1; }); }

    var checks = [];
    function add(id, section, pts, mx, message, fix) {
      checks.push({ id: id, section: section, points: pts, max: mx, ok: pts === mx, message: message, fix: fix });
    }
    var pts;

    // Headline (25)
    var hl = headline.trim().length;
    pts = (hl >= 60 && hl <= 250) ? 5 : (hl >= 30 && hl < 60 ? 2 : 0);
    add("headline_length", "Headline", pts, 5, "Headline is " + hl + " characters.",
      "Aim for 60–250 characters: role, years, top skills and one result.");
    pts = isTitle(nHead) ? 6 : 0;
    add("headline_role", "Headline", pts, 6,
      pts ? "Headline names your target role." : "Headline doesn't name your target role.",
      "Start the headline with \"" + hname + "\" so recruiter searches match it.");
    var hk = count(nHead);
    pts = hk >= 3 ? 7 : hk === 2 ? 5 : hk === 1 ? 2 : 0;
    add("headline_keywords", "Headline", pts, 7, "Headline has " + hk + " role keyword(s).",
      "Put 3–5 of your strongest skills in the headline.");
    pts = /\d/.test(headline) ? 4 : 0;
    add("headline_number", "Headline", pts, 4,
      pts ? "Headline has a number." : "Headline has no numbers.",
      "Add years of experience or a result, e.g. \"3+ years\" or \"cut costs 20%\".");
    var hf = fluffIn(headline);
    pts = hf.length ? 0 : 3;
    add("headline_fluff", "Headline", pts, 3,
      pts ? "No filler words in the headline." : "Filler words: " + hf.join(", ") + ".",
      "Replace filler with skills or results recruiters search for.");

    // Key skills (25)
    var n = skills.length;
    pts = (n >= 12 && n <= 25) ? 5 : ((n >= 8 && n <= 11) || (n >= 26 && n <= 40) ? 3 : 0);
    add("skills_count", "Key skills", pts, 5, n + " key skill(s) listed.",
      "List 12–25 specific skills. Too few limits search matches; too many dilutes them.");
    var matchedCore = role.core.filter(function (k) { return hasKw(nSkills, k); });
    var target = Math.min(8, role.core.length);
    pts = roundHalfUp(15 * Math.min(matchedCore.length, target) / target);
    add("skills_core", "Key skills", pts, 15,
      matchedCore.length + " of " + role.core.length + " core " + role.name + " skills listed.",
      "Add the missing core skills you genuinely have (see the list below).");
    var generic = skills.filter(isGeneric);
    var share = n ? generic.length / n : 0;
    pts = (n && share <= 0.2) ? 5 : (n ? 2 : 0);
    add("skills_generic", "Key skills", pts, 5,
      generic.length + " generic skill(s) like communication or MS Office.",
      "Recruiters rarely search soft skills. Swap them for tools and methods.");

    // Profile summary (20)
    var sl = summary.trim().length;
    pts = (sl >= 300 && sl <= 1000) ? 5 : ((sl >= 150 && sl < 300) || (sl > 1000 && sl <= 1500) ? 3 : 0);
    add("summary_length", "Profile summary", pts, 5, "Summary is " + sl + " characters.",
      "Aim for 300–1000 characters: 3–5 short sentences.");
    var sk = count(nSum);
    pts = sk >= 6 ? 5 : sk >= 3 ? 3 : sk >= 1 ? 1 : 0;
    add("summary_keywords", "Profile summary", pts, 5, "Summary has " + sk + " role keyword(s).",
      "Mention at least 6 role skills naturally in the summary.");
    pts = /\d/.test(summary) ? 5 : 0;
    add("summary_metrics", "Profile summary", pts, 5,
      pts ? "Summary includes numbers." : "Summary has no numbers.",
      "Add results: team size, % improvement, revenue, tickets per day, projects shipped.");
    var sf = fluffIn(summary);
    pts = !sf.length ? 5 : (sf.length === 1 ? 2 : 0);
    add("summary_fluff", "Profile summary", pts, 5,
      !sf.length ? "No filler phrases in the summary." : "Filler phrases: " + sf.join(", ") + ".",
      "Cut filler; every sentence should show a skill or a result.");

    // Employment (10)
    pts = (isTitle(nDes) || role.core.some(function (k) { return hasKw(nDes, k); })) ? 5 : 0;
    add("designation_match", "Employment", pts, 5,
      pts ? "Current designation matches the target role." : "Current designation doesn't match the target role.",
      "If your work matches the target role, describe it with the target role's words in your employment details.");
    pts = profile.resume_attached ? 5 : 0;
    add("resume_attached", "Employment", pts, 5,
      pts ? "Resume attached." : "No resume attached.",
      "Attach an up-to-date PDF resume; many recruiters download it before calling.");

    // Activity and career profile (20)
    var msg;
    if (updated === null) { pts = 0; msg = "Last update date not given."; }
    else { pts = updated <= 7 ? 10 : (updated <= 30 ? 5 : 0); msg = "Profile last updated " + Math.trunc(updated) + " day(s) ago."; }
    add("freshness", "Activity", pts, 10, msg,
      "Update something on your profile every week; recruiters often filter for recently active profiles.");
    var nl = locations.length;
    pts = (nl >= 1 && nl <= 5) ? 4 : (nl > 5 ? 2 : 0);
    add("locations", "Career profile", pts, 4, nl + " preferred location(s).",
      "Pick 1–5 cities you'd really move to, plus remote if you want it.");
    if (notice === null) { pts = 0; msg = "Notice period not given."; }
    else { pts = notice <= 30 ? 3 : 1; msg = "Notice period is " + Math.trunc(notice) + " day(s)."; }
    add("notice", "Career profile", pts, 3, msg,
      "Short notice periods get more calls. If yours is long, mention buyout or your last working day.");
    pts = profile.expected_salary ? 3 : 0;
    add("salary", "Career profile", pts, 3,
      pts ? "Expected salary filled in." : "Expected salary is empty.",
      "Fill in expected salary; recruiters filter on it.");

    var score = 0, sections = {};
    checks.forEach(function (c) {
      score += c.points;
      if (!sections[c.section]) sections[c.section] = { score: 0, max: 0 };
      sections[c.section].score += c.points;
      sections[c.section].max += c.max;
    });

    var profileText = norm([headline, summary, designation, skills.join(", ")].join(" "));
    return {
      role: { id: role.id, name: role.name },
      score: score,
      grade: score >= 80 ? "Strong" : score >= 60 ? "Average" : "Needs work",
      sections: sections,
      checks: checks,
      missing_core: role.core.filter(function (k) { return !hasKw(profileText, k); }).map(display),
      missing_extra: role.extra.filter(function (k) { return !hasKw(profileText, k); }).map(display),
      suggested_skills: suggestSkills(skills, role),
      headline_template: headlineTemplate(role, years, notice, nSkills)
    };
  }

  function suggestSkills(skills, role) {
    var keep = skills.filter(function (s) { return !isGeneric(s); });
    var have = norm(keep.join(", "));
    for (var i = 0; i < role.core.length; i++) {
      if (keep.length >= 25) break;
      if (!hasKw(have, role.core[i])) { keep.push(display(role.core[i])); have = norm(keep.join(", ")); }
    }
    return keep;
  }

  function headlineTemplate(role, years, notice, nSkills) {
    var top = role.core.filter(function (k) { return hasKw(nSkills, k); }).map(display).slice(0, 4);
    if (top.length < 4) {
      top = top.concat(role.core.map(display).filter(function (d) { return top.indexOf(d) === -1; }).slice(0, 4 - top.length));
    }
    var exp = !years ? "Fresher" : Math.trunc(years) + "+ Years";
    var p = [role.headline_name || role.name, exp, top.join(", "), "[one result with a number]"];
    if (notice !== null && notice <= 15) p.push("Immediate Joiner");
    return p.join(" | ");
  }

  return { analyze: analyze, findRole: findRole, norm: norm, asList: asList };
});
