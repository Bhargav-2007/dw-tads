import{j as e,m as M}from"./motion-DzSRPdQG.js";import{a,i as z}from"./react-Cp6UogC3.js";import{c as t,u as D,a as T,S as w,I as h,B as n,b as L,e as N}from"./index-BtJ4w0vK.js";import"./charts-UqEH7oVU.js";/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const R=t("ArrowRight",[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const q=t("EyeOff",[["path",{d:"M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49",key:"ct8e1f"}],["path",{d:"M14.084 14.158a3 3 0 0 1-4.242-4.242",key:"151rxh"}],["path",{d:"M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143",key:"13bj9a"}],["path",{d:"m2 2 20 20",key:"1ooewy"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const I=t("Eye",[["path",{d:"M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0",key:"1nclc0"}],["circle",{cx:"12",cy:"12",r:"3",key:"1v7zrd"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const U=t("LockKeyhole",[["circle",{cx:"12",cy:"16",r:"1",key:"1au0dj"}],["rect",{x:"3",y:"10",width:"18",height:"12",rx:"2",key:"6s8ecr"}],["path",{d:"M7 10V7a5 5 0 0 1 10 0v3",key:"1pqi11"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const H=t("Sparkles",[["path",{d:"M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z",key:"4pj2yx"}],["path",{d:"M20 3v4",key:"1olli1"}],["path",{d:"M22 5h-4",key:"1gvqau"}],["path",{d:"M4 17v2",key:"vumght"}],["path",{d:"M5 18H3",key:"zchphs"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const O=t("UserCheck",[["path",{d:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",key:"1yyitq"}],["circle",{cx:"9",cy:"7",r:"4",key:"nufk8"}],["polyline",{points:"16 11 18 13 22 9",key:"1pwet4"}]]);function P(){const{token:b,login:m}=D(),[p,u]=a.useState(""),[y,x]=a.useState(""),[j,g]=a.useState(""),[l,A]=a.useState(!1),[c,r]=a.useState(!1),[v,o]=a.useState(""),[C,k]=a.useState(0),S=T(),f=async s=>{sessionStorage.setItem("dwtds_demo_mode","true");const i=s==="admin"?"admin1":"analyst1";u(i),x("demo_password"),g("123456"),r(!0),o("");try{await m(i,"demo_password","123456")}catch(d){o(N(d)),k(E=>E+1)}finally{r(!1)}};return b?e.jsx(z,{to:"/timeline",replace:!0}):e.jsxs("div",{className:"login-page",role:"main",children:[e.jsxs("div",{className:"login-context",children:[e.jsx(w,{size:24}),e.jsx("span",{children:"DW-TADS / SECURE ANALYST ACCESS"})]}),e.jsxs(M.form,{className:"login-card",initial:{opacity:0,scale:S?1:.96},animate:{opacity:1,scale:1,x:!S&&v?[0,-4,4,-4,4,0]:0},transition:{duration:.3},onSubmit:async s=>{s.preventDefault(),r(!0),o("");try{await m(p,y,j)}catch(i){o(N(i)),k(d=>d+1)}finally{r(!1)}},children:[e.jsx("div",{className:"login-mark",children:e.jsx(w,{size:42})}),e.jsx("h1",{children:"DW-TADS"}),e.jsx("p",{className:"login-subtitle",children:"Dark Web Threat Actor Detection"}),e.jsx("div",{className:"login-rule"}),e.jsx(h,{label:"Username",autoComplete:"username",value:p,required:!0,onChange:s=>u(s.target.value)}),e.jsxs("div",{className:"password-field",children:[e.jsx(h,{label:"Password",type:l?"text":"password",autoComplete:"current-password",value:y,required:!0,onChange:s=>x(s.target.value)}),e.jsx(n,{type:"button",variant:"ghost","aria-label":l?"Hide password":"Show password",onClick:()=>A(s=>!s),children:l?e.jsx(q,{size:17}):e.jsx(I,{size:17})})]}),e.jsx(h,{label:"Authenticator code",className:"mono totp",placeholder:"123 456",value:j,inputMode:"numeric",autoComplete:"one-time-code",pattern:"[0-9]{6}",maxLength:6,required:!0,onChange:s=>g(s.target.value.replace(/\D/g,"").slice(0,6))}),e.jsx("p",{className:"muted text-xs",children:"Enter the 6-digit code from your authenticator."}),e.jsxs(n,{type:"submit",variant:"primary",size:"lg",loading:c,className:"full",children:["Sign in",e.jsx(R,{size:17})]}),e.jsx("div",{className:"login-error",role:"alert",children:v}),e.jsxs("div",{className:"demo-showcase-panel",children:[e.jsxs("div",{className:"demo-badge",children:[e.jsx(H,{size:14}),e.jsx("span",{children:"Interactive Showcase"})]}),e.jsx("p",{className:"demo-desc",children:"Explore live threat actor discovery, timeline investigation, graph intelligence, and audit trails."}),e.jsxs("div",{className:"demo-buttons",children:[e.jsxs(n,{type:"button",variant:"secondary",className:"demo-btn",onClick:()=>f("analyst"),disabled:c,children:[e.jsx(O,{size:14}),"Analyst Demo"]}),e.jsxs(n,{type:"button",variant:"secondary",className:"demo-btn",onClick:()=>f("admin"),disabled:c,children:[e.jsx(L,{size:14}),"Admin Demo"]})]})]}),e.jsxs("div",{className:"login-foot",children:[e.jsx(U,{size:14}),"Authorized personnel only"]})]},C),e.jsx("p",{className:"login-bottom",children:"DARK WEB THREAT ACTOR DETECTION SYSTEM"})]})}export{P as default};
