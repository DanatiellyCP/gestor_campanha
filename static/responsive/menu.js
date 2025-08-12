(function(){
  const qs=(s,p=document)=>p.querySelector(s);
  const drawer = qs('#drawer');
  const hamb = qs('#hamb');

  function toggleDrawer(){
    const open = !drawer.classList.contains('open');
    drawer.classList.toggle('open', open);
    hamb.setAttribute('aria-expanded', String(open));
  }
  if (hamb) hamb.addEventListener('click', toggleDrawer);

  // Fechar ao clicar em link (mobile)
  if (drawer){
    drawer.addEventListener('click', (e)=>{
      if (e.target.tagName === 'A') toggleDrawer();
    });
  }

  // Simulação de navegação dos CTAs (ajuste para rotas reais)
  const ctaParticipar = qs('#ctaParticipar');
  const ctaLogin = qs('#ctaLogin');
  const mParticipar = qs('#mParticipar');
  const mLogin = qs('#mLogin');
  if (ctaParticipar) ctaParticipar.addEventListener('click', ()=> console.log('CTA Participe (desktop)'));
  if (ctaLogin) ctaLogin.addEventListener('click', ()=> console.log('CTA Login (desktop)'));
  if (mParticipar) mParticipar.addEventListener('click', ()=> console.log('CTA Participe (mobile)'));
  if (mLogin) mLogin.addEventListener('click', ()=> console.log('CTA Login (mobile)'));

  // --- YouTube autoplay com áudio mediante interação ---
  const unmuteBtn = qs('#unmuteBtn');
  const iframeEl = qs('#promoVideo');
  let ytPlayer;(function(){
    const qs=(s,p=document)=>p.querySelector(s);
    const drawer = qs('#drawer');
    const hamb = qs('#hamb');
  
    function toggleDrawer(){
      const open = !drawer.classList.contains('open');
      drawer.classList.toggle('open', open);
      hamb.setAttribute('aria-expanded', String(open));
    }
    if (hamb) hamb.addEventListener('click', toggleDrawer);
  
    // Fechar ao clicar em link (mobile)
    if (drawer){
      drawer.addEventListener('click', (e)=>{
        if (e.target.tagName === 'A') toggleDrawer();
      });
    }
  
    // Simulação de navegação dos CTAs (ajuste para rotas reais)
    const ctaParticipar = qs('#ctaParticipar');
    const ctaLogin = qs('#ctaLogin');
    const mParticipar = qs('#mParticipar');
    const mLogin = qs('#mLogin');
    if (ctaParticipar) ctaParticipar.addEventListener('click', ()=> console.log('CTA Participe (desktop)'));
    if (ctaLogin) ctaLogin.addEventListener('click', ()=> console.log('CTA Login (desktop)'));
    if (mParticipar) mParticipar.addEventListener('click', ()=> console.log('CTA Participe (mobile)'));
    if (mLogin) mLogin.addEventListener('click', ()=> console.log('CTA Login (mobile)'));
  
    // --- YouTube autoplay com áudio mediante interação ---
    const unmuteBtn = qs('#unmuteBtn');
    const iframeEl = qs('#promoVideo');
    let ytPlayer;
  
    // Carrega API do YouTube
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    document.head.appendChild(tag);
  
    // Callback global exigida pela API
    window.onYouTubeIframeAPIReady = function(){
      if (!iframeEl) return;
      ytPlayer = new YT.Player('promoVideo', {
        events: {
          onReady: (e)=>{
            try{ e.target.mute(); e.target.playVideo(); }catch(_){/* noop */}
          }
        }
      });
    };
  
    // Clique para ativar som
    if (unmuteBtn){
      unmuteBtn.addEventListener('click', ()=>{
        try{
          if (ytPlayer){ ytPlayer.unMute(); ytPlayer.setVolume(100); ytPlayer.playVideo(); }
        }catch(_){/* noop */}
        unmuteBtn.style.display = 'none';
      });
    }
  })();
  
  // Privacy/Cookie banner
  (function(){
    const KEY = 'privacyAccepted:v1';
    const banner = document.getElementById('cookieBanner');
    const btn = document.getElementById('cookieAccept');
    if (!banner || !btn) return;
    try{
      const accepted = localStorage.getItem(KEY) === 'true';
      if (!accepted) banner.style.display = 'block';
      btn.addEventListener('click', function(){
        localStorage.setItem(KEY, 'true');
        banner.style.display = 'none';
      });
    }catch(e){
      // Se storage falhar, apenas mostra e permite fechar na sessão
      banner.style.display = 'block';
      btn.addEventListener('click', function(){ banner.style.display = 'none'; });
    }
  })();
  
  // Login page behaviors (CPF mask, toggle password, submit, go to register)
  (function(){
    const qs = (s,p=document)=>p.querySelector(s);
    const qsa = (s,p=document)=>Array.from(p.querySelectorAll(s));
    const form = qs('#login');
    const cpf = qs('#cpf');
    const senha = qs('#senha');
    if (!form || !cpf || !senha) return;
  
    function onlyDigits(v){ return (v||'').replace(/\D+/g,''); }
  
    cpf.addEventListener('input', e=>{
      let v = onlyDigits(e.target.value).slice(0,11);
      v = v.replace(/(\d{3})(\d)/, '$1.$2')
           .replace(/(\d{3})(\d)/, '$1.$2')
           .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
      e.target.value = v;
    });
  
    qsa('.toggle-pass').forEach(btn => {
      const target = qs('#' + btn.dataset.target);
      if (!target) return;
      btn.addEventListener('click', () => {
        const showing = target.type === 'text';
        target.type = showing ? 'password' : 'text';
        btn.textContent = showing ? '👁️' : '🙈';
        try { target.focus({ preventScroll: true }); } catch(_) { target.focus(); }
      });
    });
  
    form.addEventListener('submit', (e)=>{
      if (!form.checkValidity()){
        form.reportValidity();
        e.preventDefault();
        return;
      }
      e.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      console.log('Login:', data);
    });
  
    const goReg = qs('#goRegister');
    if (goReg){ goReg.addEventListener('click', ()=>{ window.location.href = 'form_wizard.html'; }); }
  })();
  
  // Wizard page behaviors (form_wizard.html)
  (function(){
    const qs = (s,p=document)=>p.querySelector(s);
    const qsa = (s,p=document)=>Array.from(p.querySelectorAll(s));
    const wizard = qs('#wizard');
    if (!wizard) return; // only on wizard page
  
    const panes = qsa('.step-pane');
    const stepper = qs('#stepper');
    const dots = stepper ? qsa('.dot', stepper) : [];
    const bars = stepper ? qsa('.line-bar', stepper) : [];
    const totalSteps = panes.length || 3;
    let current = 1;
  
    // Inputs
    const f = {
      nome: qs('#nome'),
      cpf: qs('#cpf'),
      email: qs('#email'),
      celular: qs('#celular'),
      nasc: qs('#nasc'),
      senha: qs('#senha'),
      senha2: qs('#senha2'),
      cep: qs('#cep'),
      estado: qs('#estado'),
      cidade: qs('#cidade'),
      logradouro: qs('#logradouro'),
      bairro: qs('#bairro'),
      numero: qs('#numero'),
      compl: qs('#compl'),
    };
  
    // Estados (UF)
    const UFs = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"];
    if (f.estado && !f.estado.dataset.filled){
      f.estado.insertAdjacentHTML('beforeend', UFs.map(uf=>`<option value="${uf}">${uf}</option>`).join(''));
      f.estado.dataset.filled = '1';
    }
  
    // Helpers
    function onlyDigits(v){ return (v||'').replace(/\D+/g,''); }
  
    // Masks
    if (f.cpf){
      f.cpf.addEventListener('input', e=>{
        let v = onlyDigits(e.target.value).slice(0,11);
        v = v.replace(/(\d{3})(\d)/, '$1.$2')
             .replace(/(\d{3})(\d)/, '$1.$2')
             .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        e.target.value = v;
      });
    }
    if (f.celular){
      f.celular.addEventListener('input', e=>{
        let v = onlyDigits(e.target.value).slice(0,11);
        v = v.replace(/^(\d{0,2})/, '($1')
             .replace(/^\((\d{2})/, '($1) ')
             .replace(/(\d{5})(\d)/, '$1-$2');
        e.target.value = v;
      });
    }
    if (f.nasc){
      f.nasc.addEventListener('input', e=>{
        let v = onlyDigits(e.target.value).slice(0,8);
        v = v.replace(/(\d{2})(\d)/, '$1/$2').replace(/(\d{2})(\d)/, '$1/$2');
        e.target.value = v;
      });
    }
  
    // CEP lookup with debounce
    let cepDebounce;
    async function lookupCEP(){
      if (!f.cep) return;
      const raw = onlyDigits(f.cep.value || '');
      if (raw.length !== 8) return;
      setCepBusy(true);
      try{
        const resp = await fetch(`https://viacep.com.br/ws/${raw}/json/`);
        if (!resp.ok) throw new Error('network');
        const data = await resp.json();
        if (data.erro){ clearAddress(); indicateCepError('CEP não encontrado.'); return; }
        fillAddressFromViaCep(data);
      }catch(err){
        clearAddress(); indicateCepError('Não foi possível consultar o CEP.');
      }finally{
        setCepBusy(false);
      }
    }
    function setCepBusy(busy){
      if (!f.cep) return;
      f.cep.toggleAttribute('aria-busy', !!busy);
      const cepField = f.cep.closest('.field');
      if (cepField) cepField.classList.toggle('loading', !!busy);
      [f.estado, f.cidade, f.logradouro, f.bairro].forEach(el=> el && el.toggleAttribute('disabled', !!busy));
    }
    function fillAddressFromViaCep(data){
      if (f.logradouro) f.logradouro.value = data.logradouro || '';
      if (f.bairro) f.bairro.value = data.bairro || '';
      if (f.cidade) f.cidade.value = data.localidade || '';
      if (f.estado) f.estado.value = data.uf || '';
    }
    function clearAddress(){
      if (f.logradouro) f.logradouro.value = '';
      if (f.cidade) f.cidade.value = '';
      if (f.estado) f.estado.value = '';
      if (f.bairro) f.bairro.value = '';
    }
    function indicateCepError(msg){
      if (!f.cep) return;
      try{ f.cep.setCustomValidity(msg); f.cep.reportValidity(); }
      finally{ setTimeout(()=> f.cep.setCustomValidity(''), 1500); }
    }
    if (f.cep){
      f.cep.addEventListener('input', e=>{
        let v = onlyDigits(e.target.value).slice(0,8);
        v = v.replace(/(\d{5})(\d)/, '$1-$2');
        e.target.value = v;
        const btnClear = qs('.clear-input[data-target="cep"]', f.cep.closest('.field'));
        if (btnClear) btnClear.classList.toggle('show', e.target.value.length > 0);
        clearTimeout(cepDebounce);
        if (e.target.value.length === 9){
          cepDebounce = setTimeout(lookupCEP, 350);
        }
      });
      f.cep.addEventListener('change', lookupCEP);
      f.cep.addEventListener('blur', lookupCEP);
      const cepClearBtn = qs('.clear-input[data-target="cep"]');
      if (cepClearBtn){
        cepClearBtn.addEventListener('click', ()=>{
          f.cep.value=''; clearTimeout(cepDebounce); clearAddress(); f.cep.focus(); cepClearBtn.classList.remove('show');
        });
      }
    }
  
    // Toggle show/hide password
    qsa('.toggle-pass').forEach(btn => {
      const target = qs('#' + btn.dataset.target);
      if (!target) return;
      btn.setAttribute('aria-pressed', 'false');
      btn.addEventListener('click', () => {
        const showing = target.type === 'text';
        target.type = showing ? 'password' : 'text';
        btn.classList.toggle('show', !showing);
        btn.setAttribute('aria-pressed', String(!showing));
        try { target.focus({ preventScroll: true }); } catch(_) { target.focus(); }
      });
    });
  
    // Password rules
    const ruleMap = {
      upper: qs('#ruleUpper'),
      lower: qs('#ruleLower'),
      number: qs('#ruleNumber'),
      len: qs('#ruleLen')
    };
    function toggleRule(el, ok){ if (!el) return; el.classList.toggle('ok', ok); el.classList.toggle('bad', !ok); }
    function evalPass(){
      if (!f.senha) return;
      const v = f.senha.value || '';
      toggleRule(ruleMap.upper, /[A-Z]/.test(v));
      toggleRule(ruleMap.lower, /[a-z]/.test(v));
      toggleRule(ruleMap.number, /\d/.test(v));
      toggleRule(ruleMap.len, v.length >= 8);
    }
    if (f.senha){ f.senha.addEventListener('input', evalPass); }
    if (f.senha2){ f.senha2.addEventListener('input', ()=>{}); }
  
    // Navigation
    const next1 = qs('#next1');
    const next2 = qs('#next2');
    const back2 = qs('#back2');
    const back3 = qs('#back3');
    function goTo(step, validator){
      if (typeof validator === 'function' && !validator()) return;
      current = Math.min(Math.max(step,1), totalSteps);
      panes.forEach(p=>p.classList.remove('active'));
      const activePane = qs(`.step-pane[data-step="${current}"]`);
      if (activePane) activePane.classList.add('active');
      const actions = activePane ? qs('.actions', activePane) : null;
      if (actions && stepper && stepper.parentElement !== actions){ actions.prepend(stepper); }
      dots.forEach((d, idx)=>{
        const n = idx+1;
        d.classList.toggle('active', n===current);
        d.classList.toggle('current', n===current);
        d.classList.toggle('done', n<current);
      });
      bars.forEach((b, idx)=>{
        b.classList.remove('fill-red','fill-yellow','partial');
        if (idx < current-1) b.classList.add('fill-red');
        else if (idx === current-1) b.classList.add('partial');
        else b.classList.add('fill-yellow');
      });
      if (stepper) stepper.setAttribute('aria-valuenow', String(current));
    }
    function validateNative(step){
      const pane = qs(`.step-pane[data-step="${step}"]`);
      const controls = qsa('input, select, textarea', pane||document.createElement('div'));
      for (const el of controls){ if (!el.checkValidity()){ el.reportValidity(); return false; } }
      return true;
    }
    if (next1) next1.addEventListener('click', ()=> goTo(2, ()=> validateNative(1)));
    if (back2) back2.addEventListener('click', ()=> goTo(1));
    if (next2) next2.addEventListener('click', ()=> goTo(3, ()=> validateNative(2)));
    if (back3) back3.addEventListener('click', ()=> goTo(2));
  
    // Initialize
    goTo(1);
  
    // Submit
    wizard.addEventListener('submit', (e)=>{
      if (!wizard.checkValidity()){ wizard.reportValidity(); e.preventDefault(); return; }
    });
  })();
  

  // Carrega API do YouTube
  const tag = document.createElement('script');
  tag.src = 'https://www.youtube.com/iframe_api';
  document.head.appendChild(tag);

  // Callback global exigida pela API
  window.onYouTubeIframeAPIReady = function(){
    if (!iframeEl) return;
    ytPlayer = new YT.Player('promoVideo', {
      events: {
        onReady: (e)=>{
          try{ e.target.mute(); e.target.playVideo(); }catch(_){/* noop */}
        }
      }
    });
  };

  // Clique para ativar som
  if (unmuteBtn){
    unmuteBtn.addEventListener('click', ()=>{
      try{
        if (ytPlayer){ ytPlayer.unMute(); ytPlayer.setVolume(100); ytPlayer.playVideo(); }
      }catch(_){/* noop */}
      unmuteBtn.style.display = 'none';
    });
  }
})();

// Privacy/Cookie banner
(function(){
  const KEY = 'privacyAccepted:v1';
  const banner = document.getElementById('cookieBanner');
  const btn = document.getElementById('cookieAccept');
  if (!banner || !btn) return;
  try{
    const accepted = localStorage.getItem(KEY) === 'true';
    if (!accepted) banner.style.display = 'block';
    btn.addEventListener('click', function(){
      localStorage.setItem(KEY, 'true');
      banner.style.display = 'none';
    });
  }catch(e){
    // Se storage falhar, apenas mostra e permite fechar na sessão
    banner.style.display = 'block';
    btn.addEventListener('click', function(){ banner.style.display = 'none'; });
  }
})();

// Login page behaviors (CPF mask, toggle password, submit, go to register)
(function(){
  const qs = (s,p=document)=>p.querySelector(s);
  const qsa = (s,p=document)=>Array.from(p.querySelectorAll(s));
  const form = qs('#login');
  const cpf = qs('#cpf');
  const senha = qs('#senha');
  if (!form || !cpf || !senha) return;

  function onlyDigits(v){ return (v||'').replace(/\D+/g,''); }

  cpf.addEventListener('input', e=>{
    let v = onlyDigits(e.target.value).slice(0,11);
    v = v.replace(/(\d{3})(\d)/, '$1.$2')
         .replace(/(\d{3})(\d)/, '$1.$2')
         .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    e.target.value = v;
  });

  qsa('.toggle-pass').forEach(btn => {
    const target = qs('#' + btn.dataset.target);
    if (!target) return;
    btn.addEventListener('click', () => {
      const showing = target.type === 'text';
      target.type = showing ? 'password' : 'text';
      btn.textContent = showing ? '👁️' : '🙈';
      try { target.focus({ preventScroll: true }); } catch(_) { target.focus(); }
    });
  });

  form.addEventListener('submit', (e)=>{
    if (!form.checkValidity()){
      form.reportValidity();
      e.preventDefault();
      return;
    }
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    console.log('Login:', data);
  });

  const goReg = qs('#goRegister');
  if (goReg){ goReg.addEventListener('click', ()=>{ window.location.href = 'form_wizard.html'; }); }
})();

// Wizard page behaviors (form_wizard.html)
(function(){
  const qs = (s,p=document)=>p.querySelector(s);
  const qsa = (s,p=document)=>Array.from(p.querySelectorAll(s));
  const wizard = qs('#wizard');
  if (!wizard) return; // only on wizard page

  const panes = qsa('.step-pane');
  const stepper = qs('#stepper');
  const dots = stepper ? qsa('.dot', stepper) : [];
  const bars = stepper ? qsa('.line-bar', stepper) : [];
  const totalSteps = panes.length || 3;
  let current = 1;

  // Inputs
  const f = {
    nome: qs('#nome'),
    cpf: qs('#cpf'),
    email: qs('#email'),
    celular: qs('#celular'),
    nasc: qs('#nasc'),
    senha: qs('#senha'),
    senha2: qs('#senha2'),
    cep: qs('#cep'),
    estado: qs('#estado'),
    cidade: qs('#cidade'),
    logradouro: qs('#logradouro'),
    bairro: qs('#bairro'),
    numero: qs('#numero'),
    compl: qs('#compl'),
  };

  // Estados (UF)
  const UFs = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"];
  if (f.estado && !f.estado.dataset.filled){
    f.estado.insertAdjacentHTML('beforeend', UFs.map(uf=>`<option value="${uf}">${uf}</option>`).join(''));
    f.estado.dataset.filled = '1';
  }

  // Helpers
  function onlyDigits(v){ return (v||'').replace(/\D+/g,''); }

  // Masks
  if (f.cpf){
    f.cpf.addEventListener('input', e=>{
      let v = onlyDigits(e.target.value).slice(0,11);
      v = v.replace(/(\d{3})(\d)/, '$1.$2')
           .replace(/(\d{3})(\d)/, '$1.$2')
           .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
      e.target.value = v;
    });
  }
  if (f.celular){
    f.celular.addEventListener('input', e=>{
      let v = onlyDigits(e.target.value).slice(0,11);
      v = v.replace(/^(\d{0,2})/, '($1')
           .replace(/^\((\d{2})/, '($1) ')
           .replace(/(\d{5})(\d)/, '$1-$2');
      e.target.value = v;
    });
  }
  if (f.nasc){
    f.nasc.addEventListener('input', e=>{
      let v = onlyDigits(e.target.value).slice(0,8);
      v = v.replace(/(\d{2})(\d)/, '$1/$2').replace(/(\d{2})(\d)/, '$1/$2');
      e.target.value = v;
    });
  }

  // CEP lookup with debounce
  let cepDebounce;
  async function lookupCEP(){
    if (!f.cep) return;
    const raw = onlyDigits(f.cep.value || '');
    if (raw.length !== 8) return;
    setCepBusy(true);
    try{
      const resp = await fetch(`https://viacep.com.br/ws/${raw}/json/`);
      if (!resp.ok) throw new Error('network');
      const data = await resp.json();
      if (data.erro){ clearAddress(); indicateCepError('CEP não encontrado.'); return; }
      fillAddressFromViaCep(data);
    }catch(err){
      clearAddress(); indicateCepError('Não foi possível consultar o CEP.');
    }finally{
      setCepBusy(false);
    }
  }
  function setCepBusy(busy){
    if (!f.cep) return;
    f.cep.toggleAttribute('aria-busy', !!busy);
    const cepField = f.cep.closest('.field');
    if (cepField) cepField.classList.toggle('loading', !!busy);
    [f.estado, f.cidade, f.logradouro, f.bairro].forEach(el=> el && el.toggleAttribute('disabled', !!busy));
  }
  function fillAddressFromViaCep(data){
    if (f.logradouro) f.logradouro.value = data.logradouro || '';
    if (f.bairro) f.bairro.value = data.bairro || '';
    if (f.cidade) f.cidade.value = data.localidade || '';
    if (f.estado) f.estado.value = data.uf || '';
  }
  function clearAddress(){
    if (f.logradouro) f.logradouro.value = '';
    if (f.cidade) f.cidade.value = '';
    if (f.estado) f.estado.value = '';
    if (f.bairro) f.bairro.value = '';
  }
  function indicateCepError(msg){
    if (!f.cep) return;
    try{ f.cep.setCustomValidity(msg); f.cep.reportValidity(); }
    finally{ setTimeout(()=> f.cep.setCustomValidity(''), 1500); }
  }
  if (f.cep){
    f.cep.addEventListener('input', e=>{
      let v = onlyDigits(e.target.value).slice(0,8);
      v = v.replace(/(\d{5})(\d)/, '$1-$2');
      e.target.value = v;
      const btnClear = qs('.clear-input[data-target="cep"]', f.cep.closest('.field'));
      if (btnClear) btnClear.classList.toggle('show', e.target.value.length > 0);
      clearTimeout(cepDebounce);
      if (e.target.value.length === 9){
        cepDebounce = setTimeout(lookupCEP, 350);
      }
    });
    f.cep.addEventListener('change', lookupCEP);
    f.cep.addEventListener('blur', lookupCEP);
    const cepClearBtn = qs('.clear-input[data-target="cep"]');
    if (cepClearBtn){
      cepClearBtn.addEventListener('click', ()=>{
        f.cep.value=''; clearTimeout(cepDebounce); clearAddress(); f.cep.focus(); cepClearBtn.classList.remove('show');
      });
    }
  }

  // Toggle show/hide password
  qsa('.toggle-pass').forEach(btn => {
    const target = qs('#' + btn.dataset.target);
    if (!target) return;
    btn.setAttribute('aria-pressed', 'false');
    btn.addEventListener('click', () => {
      const showing = target.type === 'text';
      target.type = showing ? 'password' : 'text';
      btn.classList.toggle('show', !showing);
      btn.setAttribute('aria-pressed', String(!showing));
      try { target.focus({ preventScroll: true }); } catch(_) { target.focus(); }
    });
  });

  // Password rules
  const ruleMap = {
    upper: qs('#ruleUpper'),
    lower: qs('#ruleLower'),
    number: qs('#ruleNumber'),
    len: qs('#ruleLen')
  };
  function toggleRule(el, ok){ if (!el) return; el.classList.toggle('ok', ok); el.classList.toggle('bad', !ok); }
  function evalPass(){
    if (!f.senha) return;
    const v = f.senha.value || '';
    toggleRule(ruleMap.upper, /[A-Z]/.test(v));
    toggleRule(ruleMap.lower, /[a-z]/.test(v));
    toggleRule(ruleMap.number, /\d/.test(v));
    toggleRule(ruleMap.len, v.length >= 8);
  }
  if (f.senha){ f.senha.addEventListener('input', evalPass); }
  if (f.senha2){ f.senha2.addEventListener('input', ()=>{}); }

  // Navigation
  const next1 = qs('#next1');
  const next2 = qs('#next2');
  const back2 = qs('#back2');
  const back3 = qs('#back3');
  function goTo(step, validator){
    if (typeof validator === 'function' && !validator()) return;
    current = Math.min(Math.max(step,1), totalSteps);
    panes.forEach(p=>p.classList.remove('active'));
    const activePane = qs(`.step-pane[data-step="${current}"]`);
    if (activePane) activePane.classList.add('active');
    const actions = activePane ? qs('.actions', activePane) : null;
    if (actions && stepper && stepper.parentElement !== actions){ actions.prepend(stepper); }
    dots.forEach((d, idx)=>{
      const n = idx+1;
      d.classList.toggle('active', n===current);
      d.classList.toggle('current', n===current);
      d.classList.toggle('done', n<current);
    });
    bars.forEach((b, idx)=>{
      b.classList.remove('fill-red','fill-yellow','partial');
      if (idx < current-1) b.classList.add('fill-red');
      else if (idx === current-1) b.classList.add('partial');
      else b.classList.add('fill-yellow');
    });
    if (stepper) stepper.setAttribute('aria-valuenow', String(current));
  }
  function validateNative(step){
    const pane = qs(`.step-pane[data-step="${step}"]`);
    const controls = qsa('input, select, textarea', pane||document.createElement('div'));
    for (const el of controls){ if (!el.checkValidity()){ el.reportValidity(); return false; } }
    return true;
  }
  if (next1) next1.addEventListener('click', ()=> goTo(2, ()=> validateNative(1)));
  if (back2) back2.addEventListener('click', ()=> goTo(1));
  if (next2) next2.addEventListener('click', ()=> goTo(3, ()=> validateNative(2)));
  if (back3) back3.addEventListener('click', ()=> goTo(2));

  // Initialize
  goTo(1);

  // Submit
  wizard.addEventListener('submit', (e)=>{
    if (!wizard.checkValidity()){ wizard.reportValidity(); e.preventDefault(); return; }
  });
})();
