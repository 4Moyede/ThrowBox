(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d21a3d2"],{bb51:function(e,a,t){"use strict";t.r(a);var s=function(){var e=this,a=e.$createElement,t=e._self._c||a;return t("div",[t("data-table",{attrs:{search:e.search,loadedFiles:e.getFiles,loadingData:e.dataLoading,userData:e.userInfo,currentPage:e.StoragePage,tableParams:e.params,tableHeaders:e.headers},on:{loadFiles:e.requestFiles}})],1)},i=[],n=(t("b0c0"),t("5530")),l=t("2f62"),o=t("1fdb"),r={name:"Home",props:{search:{type:String,default:""}},components:{DataTable:o["a"]},data:function(){return{userInfo:{id:"",email:""},getFiles:[],dataLoading:!0,params:{path:"",search:""},StoragePage:{isRecent:!1,sort:"name",title:"Storage"},headers:[{text:"Name",value:"name",align:"start"},{text:"Created",value:"fid",align:"end"},{text:"Size",value:"fileSize",align:"end"},{value:"action",align:"center",sortable:!1}]}},created:function(){this.requestFiles()},computed:Object(n["a"])({},Object(l["b"])({getToken:"getAccessToken"})),methods:{requestFiles:function(){var e=this;this.dataLoading=!0,console.log(this.params),this.$axios.get("/fileList/",{params:this.params}).then((function(a){e.$store.dispatch("commitTotalFileSize",a.data.totalSize),e.getFiles=a.data.fileList,e.dataLoading=!1;for(var t=0;t<e.getFiles.length;t+=1)e.getFiles[t].isFile||(e.getFiles[t].name=" ".concat(e.getFiles[t].name))})).catch((function(e){console.log(e)}))}}},c=r,d=t("2877"),g=Object(d["a"])(c,s,i,!1,null,"32adff99",null);a["default"]=g.exports}}]);
//# sourceMappingURL=chunk-2d21a3d2.8791e8d8.js.map