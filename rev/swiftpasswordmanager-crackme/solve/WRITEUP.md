Looking for usages of `Binding.onChange(_:)` in the app leads to the follow
function which is used to check the password/flag when the password field is
updated in an entry:

```
$s20SwiftPasswordManager11ContentViewV4bodyQrvg0A7CrossUI10TupleView3VyAE0E0PAEE5frame8minWidth05idealM003maxM00L6Height0nP00oP09alignmentQrSiSg_ARSdSgA2rsE9AlignmentVtFQOyAE6VStackVyAE0I5View1VyAE06EitherE0VyAGyAiEE10backgroundyQrqd__AeHRd__lFQOyAiEE7paddingyQrARFQOyAE6HStackVyAGyAiEE4fontyQrAE4FontOFQOyAE4TextV_Qo_AE6SpacerVAiEE15foregroundColoryQrAE5ColorVFQOyA9__Qo_GG_Qo__A14_Qo_AiEEA1_yQrARFQOyAWyAE0I5View6VyAWyAE0I5View2VyA15_AiEE12cornerRadiusyQrSiFQOyAE9TextFieldV_Qo_GGA29_AWyA23_yA15_A3_yA23_yA27_AE6ButtonVGGGGA29_AWyA23_yA15_A15_GGAiEEA1_yQrAE4EdgeO3SetV_ARtFQOyA31__Qo_GG_Qo_A11_GAYyAWyAGyA11_A15_A11_GGGGGG_Qo_AE08OptionalE0VyAYyAC12modalOverlay7contentQrxyXE_tAeHRzlFQOy_AYyAC14passwordDialogQrvpQOy_Qo_GQo_GGA55_yAYyACA56_A57_QrxyXE_tAeHRzlFQOy_AYyAC10errorAlertQrvpQOy_Qo_GQo_GGGyXEfU0_A51_yXEfU_A43_yXEfU0_A34_yXEfU1_A32_yXEfU_ySScfU_
```

This function implements a series of checks on the characters, mostly based on Swift String methods.

```c
char __fastcall closure #1 in closure #1 in closure #3 in closure #2 in closure #1 in closure #2 in ContentView.body.getter(
        __int64 *a1,
        _OWORD *a2)
{
  char *v3; // r12
  __int64 v4; // r13
  __int64 v5; // rbx
  Swift::String v6; // rdi
  int v7; // eax
  Swift::String v8; // rdi
  __int64 v9; // rax
  __int64 v10; // rax
  __int64 v11; // rdx
  __int64 v12; // rbx
  char v13; // r14
  __int64 v14; // rax
  __int64 v15; // rax
  __int64 v16; // rdx
  __int64 v17; // rbx
  char v18; // r14
  __int64 v19; // rax
  __int64 v20; // rax
  __int64 v21; // rdx
  __int64 v22; // rbx
  char v23; // r14
  __int64 v24; // rax
  __int64 v25; // rax
  __int64 v26; // rdx
  __int64 v27; // rbx
  char v28; // r14
  __int64 v29; // rdi
  unsigned __int64 v30; // r13
  __int64 v31; // rdx
  __int64 v32; // rbx
  __int64 v33; // rcx
  __int64 v34; // r14
  __int64 v35; // r8
  __int64 v36; // r12
  unsigned __int64 v37; // rax
  char v38; // dl
  __int64 v39; // rbx
  __int64 v40; // rdx
  __int64 v41; // r14
  __int64 v42; // rcx
  __int64 v43; // r13
  __int64 v44; // r8
  __int64 v45; // r15
  __int64 v46; // r12
  void *v47; // rdx
  void *v48; // r13
  __int64 v49; // r14
  __int64 v50; // rdx
  __int64 v51; // rbx
  char v52; // r14
  __int64 v53; // rax
  __int64 v54; // r15
  __int64 v55; // rdx
  __int64 v56; // rax
  __int64 v57; // r14
  __int64 v58; // rdx
  __int64 v59; // r12
  __int64 v60; // rax
  __int64 v61; // rdx
  __int64 v62; // rbx
  __int64 v63; // r14
  __int64 v64; // rax
  Swift::UInt64 v65; // r14
  __int64 v66; // rax
  void *v67; // rdx
  __int64 v68; // rcx
  __int64 v69; // r8
  __int64 v70; // r14
  __int64 v71; // rax
  __int64 v72; // rax
  __int64 v73; // rdx
  __int64 v74; // r14
  __int64 v75; // r14
  __int64 v76; // rax
  __int64 v77; // r12
  __int64 v78; // rdx
  __int64 v79; // rbx
  __int64 v80; // rax
  __int64 v81; // rdx
  char v82; // r14
  __int64 v83; // rax
  __int64 v84; // rax
  __int64 v85; // rdx
  __int16 v86; // bx
  __int64 v87; // rbx
  __int64 v88; // rax
  __int64 v89; // rax
  __int64 v90; // rdx
  __int16 v91; // bx
  bool v92; // cf
  char v93; // bl
  bool v94; // zf
  __int64 v95; // rbx
  __int64 v96; // rax
  __int64 v97; // rax
  __int64 v98; // rdx
  __int16 v99; // bx
  __int64 v100; // r13
  __int64 v101; // rax
  __int64 v102; // rax
  __int64 v103; // rdx
  int v104; // r14d
  __int64 v105; // rbx
  __int64 v106; // rdx
  __int64 v107; // r14
  __int16 v108; // bx
  __int64 v109; // r12
  unsigned __int8 v110; // bl
  __int64 v111; // rax
  __int64 v112; // rdx
  char v113; // r14
  __int64 v114; // r14
  __int64 v115; // rdx
  __int64 v116; // rbx
  char v117; // r14
  __int64 v118; // rsi
  __int64 v119; // r12
  __int64 v120; // rbx
  __int64 v121; // rax
  __int64 v122; // rdx
  char v123; // r14
  __int64 v124; // r14
  __int64 v125; // rbx
  __int64 v126; // rax
  __int64 v127; // rax
  __int64 v128; // rdx
  char v129; // r14
  __int64 v130; // r14
  __int64 v131; // rbx
  __int64 v132; // rax
  __int64 inited; // rax
  __int64 v134; // r15
  __int64 v135; // rbx
  __int64 v136; // rax
  __int64 v137; // r13
  __int64 v138; // rdx
  __int64 v139; // r12
  __int64 v140; // rax
  __int64 v141; // rdx
  __int64 v142; // r14
  __int64 v143; // rax
  __int64 v144; // rdx
  __int64 v145; // rbx
  __int16 v146; // r15
  __int16 v147; // r14
  __int16 v148; // bx
  __int64 v149; // r15
  unsigned __int64 v150; // rbx
  unsigned __int64 v151; // rdx
  unsigned __int64 v152; // r14
  __int64 v153; // rcx
  __int64 v154; // r13
  __int64 v155; // r8
  __int64 v156; // r12
  unsigned __int64 v157; // rax
  char v158; // dl
  void *v159; // rdx
  __int64 v160; // rcx
  __int64 v161; // r8
  __int64 v162; // rbx
  unsigned __int64 v163; // r12
  unsigned __int64 v164; // rdx
  unsigned __int64 v165; // r15
  __int64 v166; // rcx
  __int64 v167; // r13
  __int64 v168; // r8
  __int64 v169; // r14
  unsigned __int64 v170; // rax
  char v171; // dl
  __int64 v172; // rbx
  __int64 v173; // rdx
  __int64 v174; // r14
  __int64 v175; // rcx
  __int64 v176; // r15
  __int64 v177; // r8
  __int64 v178; // r12
  __int64 v179; // r14
  __int64 v180; // r14
  __int64 v181; // rax
  __int64 v182; // rax
  __int64 v183; // rdx
  char v184; // r14
  __int64 v185; // r14
  __int64 v186; // rbx
  __int64 v187; // rax
  __int64 v188; // rax
  __int64 v189; // rdx
  char v190; // r14
  __int64 v191; // r15
  __int64 v192; // r14
  unsigned __int64 v193; // rbx
  unsigned __int64 v194; // rax
  __int64 v195; // rbx
  __int64 v196; // rdx
  __int64 v197; // r14
  __int64 v198; // rcx
  __int64 v199; // r15
  __int64 v200; // r8
  __int64 v201; // r12
  __int64 v202; // r14
  __int64 v203; // rdx
  __int64 v204; // rbx
  __int64 v205; // rax
  __int64 v206; // r15
  unsigned int v207; // ecx
  unsigned int v208; // ecx
  __int64 v209; // rbx
  void *v210; // rdx
  void *v211; // r14
  Swift::String v212; // rdi
  __int64 v213; // rbx
  bool v214; // of
  __int64 v215; // r12
  __int64 v216; // r14
  __int64 v217; // rax
  unsigned __int64 v218; // rdx
  __int64 v219; // r13
  unsigned __int64 v220; // r12
  __int64 v221; // rbx
  __int64 v222; // rbx
  unsigned __int64 v223; // rax
  __int64 v224; // rax
  unsigned __int8 v225; // bl
  unsigned __int8 v226; // bl
  unsigned int v227; // eax
  unsigned int v228; // ecx
  unsigned int v229; // ecx
  int v230; // ecx
  __int64 v231; // rsi
  void *v232; // rdx
  unsigned __int64 v233; // rdx
  __int64 v234; // r12
  unsigned __int64 v235; // r13
  __int64 v236; // rbx
  __int64 v237; // rbx
  unsigned __int64 v238; // rax
  __int64 v239; // rax
  unsigned __int8 v240; // bl
  unsigned __int8 v241; // bl
  unsigned int v242; // eax
  int v243; // ecx
  __int16 v244; // r13
  __int16 v245; // bx
  __int16 v246; // r14
  unsigned __int16 v247; // cx
  _OWORD *v248; // r14
  char *v249; // r15
  __int64 v250; // r12
  __int64 v251; // rbx
  __int64 v252; // rax
  __int64 v253; // rax
  __int64 v254; // rcx
  __int64 v255; // rbx
  __int128 v256; // xmm1
  __int128 v257; // xmm2
  __int128 v258; // xmm3
  __int64 v260; // [rsp+0h] [rbp-120h] BYREF
  _OWORD *v261; // [rsp+10h] [rbp-110h]
  char *v262; // [rsp+18h] [rbp-108h]
  __int64 v263; // [rsp+20h] [rbp-100h]
  __int64 v264; // [rsp+28h] [rbp-F8h]
  __int64 v265; // [rsp+30h] [rbp-F0h]
  __int64 v266; // [rsp+38h] [rbp-E8h]
  __int64 v267; // [rsp+40h] [rbp-E0h] BYREF
  void *v268; // [rsp+48h] [rbp-D8h]
  __int64 v269; // [rsp+50h] [rbp-D0h]
  __int64 v270; // [rsp+58h] [rbp-C8h]
  __int64 v271; // [rsp+60h] [rbp-C0h]
  __int64 v272; // [rsp+68h] [rbp-B8h]
  __int64 v273; // [rsp+70h] [rbp-B0h]
  __int64 v274; // [rsp+78h] [rbp-A8h]
  __int64 v275; // [rsp+80h] [rbp-A0h] BYREF
  unsigned __int64 v276; // [rsp+88h] [rbp-98h]
  Swift::String v277; // [rsp+90h] [rbp-90h] BYREF
  __int64 v278; // [rsp+A0h] [rbp-80h]
  __int64 v279; // [rsp+A8h] [rbp-78h]
  void *v280; // [rsp+B0h] [rbp-70h]
  __int64 v281; // [rsp+B8h] [rbp-68h]
  __int64 v282; // [rsp+C0h] [rbp-60h]
  __int64 v283; // [rsp+C8h] [rbp-58h]
  __int64 v284; // [rsp+D0h] [rbp-50h]
  __int64 v285; // [rsp+D8h] [rbp-48h]
  __int64 v286; // [rsp+E0h] [rbp-40h]
  __int64 v287; // [rsp+E8h] [rbp-38h]
  __int64 v288; // [rsp+F0h] [rbp-30h]

  v3 = (char *)&v260
     - ((*(_QWORD *)(*(_QWORD *)(_swift_instantiateConcreteTypeFromMangledName(&demangling cache variable for type metadata for TaskPriority?)
                               - 8)
                   + 64LL)
       + 15LL) & 0xFFFFFFFFFFFFFFF0LL);
  v4 = a1[1];
  v5 = *a1;
  v6._countAndFlagsBits = 21828LL;
  v6._object = (void *)0xE200000000000000LL;
  LOBYTE(v7) = _sSS9hasPrefixySbSSF(v6);
  if ( (v7 & 1) == 0 )
    return v7;
  v8._countAndFlagsBits = 32046LL;
  v8._object = (void *)0xE200000000000000LL;
  LOBYTE(v7) = _sSS9hasSuffixySbSSF(v8);
  if ( (v7 & 1) == 0 )
    return v7;
  v9 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 2LL, v5, v4);
  v282 = v5;
  v10 = _sSSySJSS5IndexVcig(v9, v5, v4);
  if ( v10 ^ 0x43 | v11 ^ 0xE100000000000000LL )
  {
    v13 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
            v10,
            v11,
            67LL,
            0xE100000000000000LL,
            0LL);
    LOBYTE(v7) = swift_bridgeObjectRelease();
    v12 = v282;
    if ( (v13 & 1) == 0 )
      return v7;
  }
  else
  {
    swift_bridgeObjectRelease();
    v12 = v282;
  }
  v14 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 3LL, v12, v4);
  v15 = _sSSySJSS5IndexVcig(v14, v12, v4);
  if ( v15 ^ 0x54 | v16 ^ 0xE100000000000000LL )
  {
    v18 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
            v15,
            v16,
            84LL,
            0xE100000000000000LL,
            0LL);
    LOBYTE(v7) = swift_bridgeObjectRelease();
    v17 = v282;
    if ( (v18 & 1) == 0 )
      return v7;
  }
  else
  {
    swift_bridgeObjectRelease();
    v17 = v282;
  }
  v19 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 4LL, v17, v4);
  v20 = _sSSySJSS5IndexVcig(v19, v17, v4);
  if ( v20 ^ 0x46 | v21 ^ 0xE100000000000000LL )
  {
    v23 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
            v20,
            v21,
            70LL,
            0xE100000000000000LL,
            0LL);
    LOBYTE(v7) = swift_bridgeObjectRelease();
    v22 = v282;
    if ( (v23 & 1) == 0 )
      return v7;
  }
  else
  {
    swift_bridgeObjectRelease();
    v22 = v282;
  }
  v24 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 5LL, v22, v4);
  v25 = _sSSySJSS5IndexVcig(v24, v22, v4);
  if ( v25 ^ 0x7B | v26 ^ 0xE100000000000000LL )
  {
    v28 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
            v25,
            v26,
            123LL,
            0xE100000000000000LL,
            0LL);
    LOBYTE(v7) = swift_bridgeObjectRelease();
    v27 = v282;
    if ( (v28 & 1) == 0 )
      return v7;
  }
  else
  {
    swift_bridgeObjectRelease();
    v27 = v282;
  }
  v262 = v3;
  v261 = a2;
  swift_bridgeObjectRetain();
  v29 = v4;
  v30 = specialized Collection.dropFirst(_:)(6LL, v27, v4);
  v32 = v31;
  v34 = v33;
  v36 = v35;
  v263 = v29;
  swift_bridgeObjectRelease();
  v37 = _sSs5index_8offsetBy07limitedC0SS5IndexVSgAE_SiAEtF(v32, -2LL, v30, v30, v32, v34, v36);
  if ( (v38 & 1) != 0 )
    v37 = v30;
  if ( v37 >> 14 < v30 >> 14 )
    BUG();
  v39 = _sSsySsSnySS5IndexVGcig(v30, v37, v30, v32, v34, v36);
  v41 = v40;
  v43 = v42;
  v45 = v44;
  swift_bridgeObjectRelease();
  v46 = _sSS14_fromSubstringySSSshFZ(v39, v41, v43, v45);
  v48 = v47;
  swift_bridgeObjectRelease();
  if ( _sSS5countSivg(v46, v48) != 29 )
    goto LABEL_28;
  swift_bridgeObjectRetain();
  v49 = specialized BidirectionalCollection.last.getter(v46, v48);
  v51 = v50;
  swift_bridgeObjectRelease();
  if ( !v51 )
    goto LABEL_28;
  if ( !(v49 ^ 0x2E | v51 ^ 0xE100000000000000LL) )
  {
    swift_bridgeObjectRelease();
    goto LABEL_23;
  }
  v52 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
          v49,
          v51,
          46LL,
          0xE100000000000000LL,
          0LL);
  swift_bridgeObjectRelease();
  if ( (v52 & 1) == 0 )
  {
LABEL_28:
    LOBYTE(v7) = swift_bridgeObjectRelease();
    return v7;
  }
LABEL_23:
  v53 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 2LL, v46, v48);
  v264 = _sSSySJSS5IndexVcig(v53, v46, v48);
  v54 = v46;
  v287 = v55;
  v56 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 6LL, v46, v48);
  v57 = _sSSySJSS5IndexVcig(v56, v46, v48);
  v59 = v58;
  v60 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 8LL, v54, v48);
  v265 = _sSSySJSS5IndexVcig(v60, v54, v48);
  v62 = v61;
  if ( (unsigned int)String.h()() != -661603659 )
  {
    swift_bridgeObjectRelease();
    swift_bridgeObjectRelease();
    swift_bridgeObjectRelease();
    goto LABEL_28;
  }
  v286 = v62;
  v284 = v59;
  v266 = v57;
  v267 = v54;
  v268 = v48;
  swift_bridgeObjectRetain();
  v63 = _swift_instantiateConcreteTypeFromMangledName(&demangling cache variable for type metadata for ReversedCollection<String>);
  v64 = lazy protocol witness table accessor for type WindowGroup<TupleView1<HotReloadableView>> and conformance WindowGroup<A>(
          &lazy protocol witness table cache variable for type ReversedCollection<String> and conformance ReversedCollection<A>,
          &demangling cache variable for type metadata for ReversedCollection<String>,
          &protocol conformance descriptor for ReversedCollection<A>);
  _sSSySSxcSTRzSJ7ElementRtzlufC(&v267, v63, v64);
  v65 = String.h()();
  swift_bridgeObjectRelease();
  if ( HIDWORD(v65) != -2132978810 )
    goto LABEL_59;
  v66 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 8LL, v54, v48);
  v285 = v54;
  v288 = (__int64)v48;
  _sSSySsSnySS5IndexVGcig(15LL, v66, v54, v48);
  v268 = v67;
  v269 = v68;
  v270 = v69;
  v70 = _swift_instantiateConcreteTypeFromMangledName(&demangling cache variable for type metadata for ReversedCollection<Substring>);
  v71 = lazy protocol witness table accessor for type WindowGroup<TupleView1<HotReloadableView>> and conformance WindowGroup<A>(
          &lazy protocol witness table cache variable for type ReversedCollection<Substring> and conformance ReversedCollection<A>,
          &demangling cache variable for type metadata for ReversedCollection<Substring>,
          &protocol conformance descriptor for ReversedCollection<A>);
  v72 = _sSSySSxcSTRzSJ7ElementRtzlufC(&v267, v70, v71);
  v74 = specialized Sequence.compactMap<A>(_:)(v72, v73);
  v281 = 0LL;
  swift_bridgeObjectRelease();
  v267 = v74;
  v75 = _swift_instantiateConcreteTypeFromMangledName(&demangling cache variable for type metadata for [Character]);
  v76 = lazy protocol witness table accessor for type WindowGroup<TupleView1<HotReloadableView>> and conformance WindowGroup<A>(
          &lazy protocol witness table cache variable for type [Character] and conformance [A],
          &demangling cache variable for type metadata for [Character],
          &protocol conformance descriptor for [A]);
  v280 = (void *)v75;
  v279 = v76;
  v77 = _sSSySSxcSTRzSJ7ElementRtzlufC(&v267, v75, v76);
  v79 = v78;
  v80 = specialized Collection.first.getter(v77, v78);
  if ( !v81 )
    goto LABEL_47;
  v283 = v79;
  if ( v80 ^ 0x67 | v81 ^ 0xE100000000000000LL )
  {
    v82 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
            v80,
            v81,
            103LL,
            0xE100000000000000LL,
            0LL);
    swift_bridgeObjectRelease();
    v79 = v283;
    if ( (v82 & 1) == 0 )
      goto LABEL_47;
  }
  else
  {
    swift_bridgeObjectRelease();
  }
  v83 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 1LL, v77, v79);
  v84 = _sSSySJSS5IndexVcig(v83, v77, v79);
  v86 = _sSJ10asciiValues5UInt8VSgvg(v84, v85);
  swift_bridgeObjectRelease();
  if ( (v86 & 0x100) != 0 )
    BUG();
  if ( (_BYTE)v86 != 105 )
    goto LABEL_46;
  v87 = v283;
  v88 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 2LL, v77, v283);
  v89 = _sSSySJSS5IndexVcig(v88, v77, v87);
  v91 = _sSJ10asciiValues5UInt8VSgvg(v89, v90);
  swift_bridgeObjectRelease();
  if ( (v91 & 0x100) != 0 )
    BUG();
  v92 = __CFADD__((_BYTE)v91, 111);
  v93 = v91 + 111;
  if ( v92 )
    BUG();
  v94 = v93 == -97;
  v95 = v283;
  if ( !v94 )
  {
LABEL_47:
    swift_bridgeObjectRelease();
    swift_bridgeObjectRelease();
    swift_bridgeObjectRelease();
    swift_bridgeObjectRelease();
LABEL_48:
    LOBYTE(v7) = swift_bridgeObjectRelease();
    return v7;
  }
  v96 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 3LL, v77, v283);
  v97 = _sSSySJSS5IndexVcig(v96, v77, v95);
  v99 = _sSJ10asciiValues5UInt8VSgvg(v97, v98);
  swift_bridgeObjectRelease();
  if ( (v99 & 0x100) != 0 )
    BUG();
  if ( (v99 & 1) != 0 )
  {
LABEL_46:
    swift_bridgeObjectRelease();
    swift_bridgeObjectRelease();
    swift_bridgeObjectRelease();
LABEL_60:
    swift_bridgeObjectRelease();
    goto LABEL_48;
  }
  v100 = v283;
  v101 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 3LL, v77, v283);
  v102 = _sSSySJSS5IndexVcig(v101, v77, v100);
  v104 = _sSJ10asciiValues5UInt8VSgvg(v102, v103);
  swift_bridgeObjectRelease();
  LODWORD(v278) = v104;
  if ( (v104 & 0x100) != 0 )
    BUG();
  v105 = specialized Collection.first.getter(v77, v100);
  v107 = v106;
  swift_bridgeObjectRelease();
  if ( !v107 )
    BUG();
  v108 = _sSJ10asciiValues5UInt8VSgvg(v105, v107);
  swift_bridgeObjectRelease();
  v109 = v288;
  if ( (v108 & 0x100) != 0 )
    BUG();
  v92 = __CFADD__((_BYTE)v278, (_BYTE)v108);
  v110 = v278 + v108;
  if ( v92 )
    BUG();
  v267 = v110 >> 1;
  v111 = _sSS18_uncheckedFromUTF8ySSSRys5UInt8VGFZ(&v267, 1LL);
  if ( v111 ^ 0x67 | v112 ^ 0xE100000000000000LL )
  {
    v113 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
             v111,
             v112,
             103LL,
             0xE100000000000000LL,
             0LL);
    swift_bridgeObjectRelease();
    if ( (v113 & 1) == 0 )
      goto LABEL_59;
  }
  else
  {
    swift_bridgeObjectRelease();
  }
  swift_bridgeObjectRetain();
  v114 = specialized Collection.first.getter(v285, v109);
  v116 = v115;
  swift_bridgeObjectRelease();
  if ( !v116 )
    goto LABEL_59;
  if ( v114 ^ 0x63 | v116 ^ 0xE100000000000000LL )
  {
    v117 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
             v114,
             v116,
             99LL,
             0xE100000000000000LL,
             0LL);
    swift_bridgeObjectRelease();
    if ( (v117 & 1) == 0 )
      goto LABEL_59;
  }
  else
  {
    swift_bridgeObjectRelease();
  }
  swift_bridgeObjectRetain();
  v118 = v109;
  v119 = v281;
  v120 = specialized Sequence.compactMap<A>(_:)(v285, v118);
  swift_bridgeObjectRelease();
  v267 = v120;
  v121 = _sSSySSxcSTRzSJ7ElementRtzlufC(&v267, v280, v279);
  if ( v121 ^ 0x6735 | v122 ^ 0xE200000000000000LL )
  {
    v123 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
             v121,
             v122,
             26421LL,
             0xE200000000000000LL,
             0LL);
    swift_bridgeObjectRelease();
    if ( (v123 & 1) == 0 )
      goto LABEL_59;
  }
  else
  {
    swift_bridgeObjectRelease();
  }
  v124 = v285;
  v125 = v288;
  v126 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 27LL, v285, v288);
  v127 = _sSSySJSS5IndexVcig(v126, v124, v125);
  if ( v127 ^ 0x2E | v128 ^ 0xE100000000000000LL )
  {
    v129 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
             v127,
             v128,
             46LL,
             0xE100000000000000LL,
             0LL);
    swift_bridgeObjectRelease();
    if ( (v129 & 1) == 0 )
      goto LABEL_59;
  }
  else
  {
    swift_bridgeObjectRelease();
  }
  v130 = v288;
  swift_bridgeObjectRetain();
  v131 = specialized Sequence.compactMap<A>(_:)(1LL, 5LL, v285, v130);
  v283 = v119;
  swift_bridgeObjectRelease();
  v132 = _swift_instantiateConcreteTypeFromMangledName(&demangling cache variable for type metadata for _ContiguousArrayStorage<UInt64>);
  inited = swift_initStaticObject(v132, &unk_562D40);
  LOBYTE(v130) = _sSasSQRzlE2eeoiySbSayxG_ABtFZs6UInt64V_Tt1g5(v131, inited);
  swift_release();
  if ( (v130 & 1) == 0 )
    goto LABEL_59;
  v134 = v285;
  v135 = v288;
  v136 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 14LL, v285, v288);
  v137 = _sSSySJSS5IndexVcig(v136, v134, v135);
  v139 = v138;
  v140 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 15LL, v134, v135);
  v280 = (void *)_sSSySJSS5IndexVcig(v140, v134, v135);
  v142 = v141;
  v143 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 24LL, v134, v135);
  v281 = _sSSySJSS5IndexVcig(v143, v134, v135);
  v145 = v144;
  v146 = _sSJ10asciiValues5UInt8VSgvg(v137, v139);
  swift_bridgeObjectRelease();
  if ( (v146 & 0x100) != 0 )
    BUG();
  v147 = _sSJ10asciiValues5UInt8VSgvg(v280, v142);
  swift_bridgeObjectRelease();
  if ( (v147 & 0x100) != 0 )
    BUG();
  v148 = _sSJ10asciiValues5UInt8VSgvg(v281, v145);
  swift_bridgeObjectRelease();
  if ( (v148 & 0x100) != 0 )
    BUG();
  if ( (unsigned __int8)v146 + 2 * (unsigned __int8)v147 + 3 * (unsigned __int8)v148 != 383
    || 5 * (unsigned __int8)v147 + 4 * (unsigned __int8)v146 + 6 * (unsigned __int8)v148 != 959
    || 9 * ((unsigned __int8)v146 + (unsigned __int8)v148) + 8 * (unsigned __int8)v147 != 1641 )
  {
    goto LABEL_59;
  }
  v149 = v288;
  swift_bridgeObjectRetain();
  v150 = specialized Collection.dropFirst(_:)(10LL, v285, v149);
  v152 = v151;
  v154 = v153;
  v156 = v155;
  swift_bridgeObjectRelease();
  v157 = _sSs5index_8offsetBy07limitedC0SS5IndexVSgAE_SiAEtF(v150, 4LL, v152, v150, v152, v154, v156);
  if ( (v158 & 1) != 0 )
    v157 = v152;
  if ( v157 >> 14 < v150 >> 14 )
    BUG();
  v278 = _sSsySsSnySS5IndexVGcig(v150, v157, v150, v152, v154, v156);
  v280 = v159;
  v281 = v160;
  v279 = v161;
  swift_bridgeObjectRelease();
  v162 = v288;
  swift_bridgeObjectRetain();
  v163 = specialized Collection.dropFirst(_:)(20LL, v285, v162);
  v165 = v164;
  v167 = v166;
  v169 = v168;
  swift_bridgeObjectRelease();
  v170 = _sSs5index_8offsetBy07limitedC0SS5IndexVSgAE_SiAEtF(v163, 4LL, v165, v163, v165, v167, v169);
  if ( (v171 & 1) != 0 )
    v170 = v165;
  if ( v170 >> 14 < v163 >> 14 )
    BUG();
  v172 = _sSsySsSnySS5IndexVGcig(v163, v170, v163, v165, v167, v169);
  v174 = v173;
  v176 = v175;
  v178 = v177;
  swift_bridgeObjectRelease();
  v267 = v278;
  v268 = v280;
  v269 = v281;
  v270 = v279;
  v271 = v172;
  v272 = v174;
  v273 = v176;
  v274 = v178;
  v179 = specialized Sequence.flatMap<A>(_:)(&v267);
  outlined release of Zip2Sequence<Substring, Substring>(&v267);
  v275 = v179;
  v180 = _swift_instantiateConcreteTypeFromMangledName(&demangling cache variable for type metadata for ReversedCollection<[Character]>);
  v181 = lazy protocol witness table accessor for type WindowGroup<TupleView1<HotReloadableView>> and conformance WindowGroup<A>(
           &lazy protocol witness table cache variable for type ReversedCollection<[Character]> and conformance ReversedCollection<A>,
           &demangling cache variable for type metadata for ReversedCollection<[Character]>,
           &protocol conformance descriptor for ReversedCollection<A>);
  v182 = _sSSySSxcSTRzSJ7ElementRtzlufC(&v275, v180, v181);
  if ( v182 ^ 0x5F317035345F7368LL | v183 ^ 0xE800000000000000LL )
  {
    v184 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
             v182,
             v183,
             0x5F317035345F7368LL,
             0xE800000000000000LL,
             0LL);
    swift_bridgeObjectRelease();
    if ( (v184 & 1) == 0 )
      goto LABEL_59;
  }
  else
  {
    swift_bridgeObjectRelease();
  }
  v185 = v285;
  v186 = v288;
  v187 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 26LL, v285, v288);
  v188 = _sSSySJSS5IndexVcig(v187, v185, v186);
  if ( !(v188 ^ 0x64 | v189 ^ 0xE100000000000000LL) )
  {
    swift_bridgeObjectRelease();
    goto LABEL_85;
  }
  v190 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
           v188,
           v189,
           100LL,
           0xE100000000000000LL,
           0LL);
  swift_bridgeObjectRelease();
  if ( (v190 & 1) == 0 )
  {
LABEL_59:
    swift_bridgeObjectRelease();
    swift_bridgeObjectRelease();
    goto LABEL_60;
  }
LABEL_85:
  v191 = v285;
  v192 = v288;
  v193 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 16LL, v285, v288);
  v194 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 20LL, v191, v192);
  if ( v194 >> 14 < v193 >> 14 )
    BUG();
  v195 = _sSSySsSnySS5IndexVGcig(v193, v194, v285, v288);
  v197 = v196;
  v199 = v198;
  v201 = v200;
  swift_bridgeObjectRelease();
  v202 = _sSS14_fromSubstringySSSshFZ(v195, v197, v199, v201);
  v204 = v203;
  swift_bridgeObjectRelease();
  v275 = 0LL;
  v276 = 0xE000000000000000LL;
  v283 = v202;
  v288 = v204;
  v205 = _sSS5countSivg(v202, v204);
  v279 = v205 - 1;
  if ( __OFSUB__(v205, 1LL) )
    BUG();
  if ( v279 > 0 )
  {
    v206 = 0LL;
    do
    {
      v213 = v206;
      v214 = __OFADD__(2LL, v206);
      v206 += 2LL;
      if ( v214 )
        v206 = 0x7FFFFFFFFFFFFFFFLL;
      v215 = v283;
      v216 = v288;
      v285 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, v213, v283, v288);
      v217 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, v213 + 1, v215, v216);
      v219 = _sSSySJSS5IndexVcig(v217, v215, v216);
      v220 = v218;
      if ( !(v219 ^ 0xA0D | v218 ^ 0xE200000000000000LL)
        || (_ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
              v219,
              v218,
              2573LL,
              0xE200000000000000LL,
              0LL) & 1) != 0 )
      {
        swift_bridgeObjectRelease();
        LOBYTE(v221) = 10;
      }
      else
      {
        v222 = HIBYTE(v220) & 0xF;
        if ( (v220 & 0x2000000000000000LL) == 0 )
          v222 = v219 & 0xFFFFFFFFFFFFLL;
        if ( !v222 )
          BUG();
        if ( (v220 & 0x1000000000000000LL) != 0 )
          v223 = _sSS17UnicodeScalarViewV13_foreignIndex5afterSS0E0VAF_tF(15LL, v219, v220);
        else
          v223 = _ss11_StringGutsV20fastUTF8ScalarLength10startingAtS2i_tF(0LL) << 16;
        if ( v223 >> 14 != 4 * v222 )
          goto LABEL_148;
        v224 = specialized Collection.first.getter(v219, v220);
        if ( (v224 & 0x100000000LL) != 0 )
          BUG();
        if ( (v224 & 0xFFFFFF80) != 0 )
        {
LABEL_148:
          swift_bridgeObjectRelease();
          BUG();
        }
        v221 = specialized Collection.first.getter(v219, v220);
        if ( (v221 & 0x100000000LL) != 0 )
          BUG();
        swift_bridgeObjectRelease();
        if ( (v221 & 0xFFFFFF00) != 0 )
          BUG();
      }
      v92 = (_BYTE)v221 == 0;
      v225 = v221 - 1;
      if ( v92 )
        BUG();
      if ( (v225 & 0x80u) != 0 )
      {
        v230 = (v225 & 0x3F) << 8;
        v227 = v230 + (v225 >> 6) + 33217;
        if ( v230 + (v225 >> 6) == -33217 )
        {
LABEL_112:
          v229 = 32;
          goto LABEL_113;
        }
      }
      else
      {
        v226 = v225 + 1;
        v227 = v226;
        if ( !v226 )
          goto LABEL_112;
      }
      _BitScanReverse(&v228, v227);
      v229 = v228 ^ 0x1F;
LABEL_113:
      v231 = 4LL - (v229 >> 3);
      v277._countAndFlagsBits = ~(-1LL << (8 * (unsigned __int8)v231)) & (v227 + 0xFEFEFEFEFEFEFFLL);
      v281 = _sSS18_uncheckedFromUTF8ySSSRys5UInt8VGFZ(&v277, v231);
      v280 = v232;
      v234 = _sSSySJSS5IndexVcig(v285, v283, v288);
      v235 = v233;
      if ( !(v234 ^ 0xA0D | v233 ^ 0xE200000000000000LL)
        || (_ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
              v234,
              v233,
              2573LL,
              0xE200000000000000LL,
              0LL) & 1) != 0 )
      {
        swift_bridgeObjectRelease();
        LOBYTE(v236) = 10;
      }
      else
      {
        v237 = HIBYTE(v235) & 0xF;
        if ( (v235 & 0x2000000000000000LL) == 0 )
          v237 = v234 & 0xFFFFFFFFFFFFLL;
        if ( !v237 )
          BUG();
        if ( (v235 & 0x1000000000000000LL) != 0 )
          v238 = _sSS17UnicodeScalarViewV13_foreignIndex5afterSS0E0VAF_tF(15LL, v234, v235);
        else
          v238 = _ss11_StringGutsV20fastUTF8ScalarLength10startingAtS2i_tF(0LL) << 16;
        if ( v238 >> 14 != 4 * v237 )
          goto LABEL_149;
        v239 = specialized Collection.first.getter(v234, v235);
        if ( (v239 & 0x100000000LL) != 0 )
          BUG();
        if ( (v239 & 0xFFFFFF80) != 0 )
        {
LABEL_149:
          swift_bridgeObjectRelease();
          BUG();
        }
        v236 = specialized Collection.first.getter(v234, v235);
        if ( (v236 & 0x100000000LL) != 0 )
          BUG();
        swift_bridgeObjectRelease();
        if ( (v236 & 0xFFFFFF00) != 0 )
          BUG();
      }
      v240 = v236 + 1;
      if ( !v240 )
        BUG();
      if ( (v240 & 0x80u) != 0 )
      {
        v243 = (v240 & 0x3F) << 8;
        v242 = v243 + (v240 >> 6) + 33217;
        if ( v243 + (v240 >> 6) == -33217 )
        {
LABEL_129:
          v208 = 32;
          goto LABEL_91;
        }
      }
      else
      {
        v241 = v240 + 1;
        v242 = v241;
        if ( !v241 )
          goto LABEL_129;
      }
      _BitScanReverse(&v207, v242);
      v208 = v207 ^ 0x1F;
LABEL_91:
      v209 = _sSS18_uncheckedFromUTF8ySSSRys5UInt8VGFZ(&v277, 4LL - (v208 >> 3));
      v211 = v210;
      v277._countAndFlagsBits = v281;
      v277._object = v280;
      swift_bridgeObjectRetain();
      v212._countAndFlagsBits = v209;
      v212._object = v211;
      _sSS6appendyySSF(v212);
      swift_bridgeObjectRelease();
      swift_bridgeObjectRelease();
      _sSS6appendyySSF(v277);
      swift_bridgeObjectRelease();
    }
    while ( v206 < v279 );
  }
  swift_bridgeObjectRelease();
  if ( v275 ^ 0x655E3171 | v276 ^ 0xE400000000000000LL
    && (_ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
          v275,
          v276,
          1700671857LL,
          0xE400000000000000LL,
          0LL) & 1) == 0 )
  {
    goto LABEL_59;
  }
  v244 = _sSJ10asciiValues5UInt8VSgvg(v264, v287);
  swift_bridgeObjectRelease();
  if ( (v244 & 0x100) != 0 )
    BUG();
  v245 = _sSJ10asciiValues5UInt8VSgvg(v266, v284);
  swift_bridgeObjectRelease();
  if ( (v245 & 0x100) != 0 )
    BUG();
  v246 = _sSJ10asciiValues5UInt8VSgvg(v265, v286);
  swift_bridgeObjectRelease();
  if ( (v246 & 0x100) != 0 )
    BUG();
  swift_bridgeObjectRelease();
  LOBYTE(v7) = v244;
  v247 = (unsigned __int8)v246;
  if ( (unsigned __int8)v244 + 2 * (unsigned __int8)v245 + 3 * (unsigned __int8)v246 == 552 )
  {
    LOBYTE(v7) = v245;
    if ( 5 * (unsigned __int8)v245 + 4 * (unsigned __int8)v244 + 6 * (unsigned __int8)v246 == 1404 )
    {
      v7 = 6 * (unsigned __int8)v244 + 8 * (unsigned __int8)v245;
      v248 = v261;
      v249 = v262;
      v250 = v263;
      v251 = v282;
      if ( v7 + 9 * v247 == 2145 )
      {
        v252 = _sScPMa(0LL);
        (*(void (__fastcall **)(char *, __int64, __int64, __int64))(*(_QWORD *)(v252 - 8) + 56LL))(v249, 1LL, 1LL, v252);
        v253 = swift_allocObject(&unk_54ABA0, 160LL, 7LL);
        v254 = v251;
        v255 = v253;
        *(_OWORD *)(v253 + 16) = 0LL;
        v256 = v248[1];
        v257 = v248[2];
        v258 = v248[3];
        *(_OWORD *)(v253 + 32) = *v248;
        *(_OWORD *)(v253 + 48) = v256;
        *(_OWORD *)(v253 + 64) = v257;
        *(_OWORD *)(v253 + 80) = v258;
        *(_OWORD *)(v253 + 96) = v248[4];
        *(_OWORD *)(v253 + 112) = v248[5];
        *(_OWORD *)(v253 + 128) = v248[6];
        *(_QWORD *)(v253 + 144) = v254;
        *(_QWORD *)(v253 + 152) = v250;
        swift_bridgeObjectRetain();
        outlined retain of ContentView(v248);
        _sScTss5NeverORs_rlE8priority9operationScTyxABGScPSg_xyYaYAcntcfCSi_Tt1g5Tm(
          v249,
          &async function pointer to partial apply for closure #1 in closure #1 in closure #1 in closure #3 in closure #2 in closure #1 in closure #2 in ContentView.body.getter,
          v255,
          &unk_54A970,
          &type metadata for Int,
          &_sxIeAgHr_xs5Error_pIegHrzo_s8SendableRzs5NeverORs_r0_lTRSi_TG5TATu);
        LOBYTE(v7) = swift_release();
      }
    }
  }
  return v7;
}
```

e.g. the following checks that the char at index 2 is a `C`

```c
  v9 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 2LL, v5, v4);
  v282 = v5;
  v10 = _sSSySJSS5IndexVcig(v9, v5, v4);
  if ( v10 ^ 'C' | v11 ^ 0xE100000000000000LL )
  {
    v13 = _ss27_stringCompareWithSmolCheck__9expectingSbs11_StringGutsV_ADs01_G16ComparisonResultOtF(
            v10,
            v11,
            67LL,
            0xE100000000000000LL,
            0LL);
    LOBYTE(v7) = swift_bridgeObjectRelease();
    v12 = v282;
    if ( (v13 & 1) == 0 )
      return v7;
  }
  else
  {
    swift_bridgeObjectRelease();
    v12 = v282;
  }
```

e.g. the following checks that the characters at index 14, 15, and 24 satisfy

```
1*flag14 + 2*flag15 + 3*flag24 == 383
4*flag14 + 5*flag15 + 6*flag24 == 959
9*flag14 + 8*flag15 + 9*flag24 == 1641
```

```c
  v136 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 14LL, v285, v288);
  v137 = _sSSySJSS5IndexVcig(v136, v134, v135);
  v139 = v138;
  v140 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 15LL, v134, v135);
  v280 = (void *)_sSSySJSS5IndexVcig(v140, v134, v135);
  v142 = v141;
  v143 = _sSS5index_8offsetBySS5IndexVAD_SitF(15LL, 24LL, v134, v135);
  v281 = _sSSySJSS5IndexVcig(v143, v134, v135);
  v145 = v144;
  v146 = _sSJ10asciiValues5UInt8VSgvg(v137, v139);
  swift_bridgeObjectRelease();
  if ( (v146 & 0x100) != 0 )
    BUG();
  v147 = _sSJ10asciiValues5UInt8VSgvg(v280, v142);
  swift_bridgeObjectRelease();
  if ( (v147 & 0x100) != 0 )
    BUG();
  v148 = _sSJ10asciiValues5UInt8VSgvg(v281, v145);
  swift_bridgeObjectRelease();
  if ( (v148 & 0x100) != 0 )
    BUG();
  if ( (unsigned __int8)v146 + 2 * (unsigned __int8)v147 + 3 * (unsigned __int8)v148 != 383
    || 5 * (unsigned __int8)v147 + 4 * (unsigned __int8)v146 + 6 * (unsigned __int8)v148 != 959
    || 9 * ((unsigned __int8)v146 + (unsigned __int8)v148) + 8 * (unsigned __int8)v147 != 1641 )
  {
    goto LABEL_59;
  }
```
