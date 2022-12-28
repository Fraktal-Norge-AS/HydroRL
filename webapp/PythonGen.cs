using DKWebapp.Models.ApiPoco;
using System.Reflection;
using System;
using System.Linq;
using System.IO;
using System.Collections.Generic;
public class PythonGen
{
    private string nameSpace;
    public PythonGen(string outpath){

        Type type = typeof(ApiObject);
        this.nameSpace = type.Namespace;

        var allTypes = from t in type.Assembly.GetTypes()
                        where t.Namespace == this.nameSpace
                        select t;

        using(StreamWriter writer = new StreamWriter(outpath))
        {
            writer.WriteLine("import pandas as pd");
            writer.WriteLine("import json");
            writer.WriteLine("from enum import Enum");
            writer.WriteLine();
            
            foreach(var t in allTypes)
                GenPythonWrapper(t, new IdentWriter(writer));
        }
    }

    private void GenPythonWrapper(Type t, IdentWriter writer)
    {
        if(t.IsClass && !t.IsAbstract)
            GenPythonClassWrapper(t, writer);
        else if(t.IsEnum)
            GenPythonEnumWrapper(t, writer);
    }

    private string CamelCase(string name)
    {
        return Char.ToLowerInvariant(name[0]) + name.Substring(1);
    }

    private bool IsPrimitive(Type t)
    {
        if(t.IsGenericType) return false;
        return t.Namespace != this.nameSpace;
    }

    private bool IsNullable(Type t)
    {
        return Nullable.GetUnderlyingType(t) != null;
    }

    private bool IsCollection(Type t)
    {
        return t.IsGenericType && t.GetGenericTypeDefinition() == typeof(List<>);
    }
    private bool IsDictionary(Type t)
    {
        return t.IsGenericType && t.GetGenericTypeDefinition() == typeof(Dictionary<,>);
    }

    private bool IsSimpleCollection(Type t)
    {
        return IsCollection(t) && IsPrimitive(t.GetGenericArguments()[0]);
    }

    private bool IsApiType(Type t)
    {
        return t.Namespace == this.nameSpace;
    }

    private bool IsApiCollection(Type t)
    {
        return IsCollection(t) && IsApiType(t.GetGenericArguments()[0]);
    }

    private string Q(string s)
    {
        return "\"" + s + "\"";
    }

    private void GenPythonEnumWrapper(Type t, IdentWriter writer)
    {
        writer.WriteLine("class " + t.Name + "(Enum):");
        writer.ident ++;

        foreach (var item in Enum.GetValues(t))
        {
            string enumName = item.ToString();
            if(enumName == "None") enumName = "Non";

            writer.WriteLine(enumName + " = " + Q(item.ToString()));
        }
        writer.WriteLine();
    }

    private void PrintConvertMethods(IdentWriter writer)
    {
        writer.WriteLine();
        writer.WriteLine("def to_pandas(self):");
        writer.ident ++;
        writer.WriteLine("return pd.json_normalize(self.to_dict())");
        writer.ident --;

        writer.WriteLine();
        writer.WriteLine("def __str__(self):");
        writer.ident ++;
        writer.WriteLine("return str(self.to_pandas())");
        writer.ident --;

        writer.WriteLine();
        writer.WriteLine("def to_json(self):");
        writer.ident ++;
        writer.WriteLine("return json.dumps(self.to_dict(), indent = 4, ensure_ascii=False)");
        writer.ident --;

        writer.WriteLine();
        writer.WriteLine("def _repr_html_(self):");
        writer.ident ++;
        writer.WriteLine(" return self.to_pandas()._repr_html_()");
        writer.ident --;
    }

    private void GenPythonClassWrapper(Type t, IdentWriter writer)
    {
        writer.WriteLine("class " + t.Name + ":");
        writer.ident ++;
        writer.WriteLine("def __init__(self, json):");
        writer.ident ++;

        foreach (var member in t.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            string memberName = CamelCase(member.Name);
            string propAccess = "json[" + Q(memberName) + "]";
            
            if(member.PropertyType.IsEnum){
                writer.WriteLine("self." + memberName + " = " + member.PropertyType.Name + "[" + propAccess + "]" );
            }else if(IsPrimitive(member.PropertyType)){
                writer.WriteLine("self." + memberName + " = " + propAccess );
            }else if(IsNullable(member.PropertyType) || IsSimpleCollection(member.PropertyType) || IsDictionary(member.PropertyType)){
                string text = "self." + memberName + " = None if not " + Q(memberName) + " in json else " + propAccess;
                writer.WriteLine(text);
            }else if(IsApiType(member.PropertyType)){
                writer.WriteLine("self." + memberName + " = " + member.PropertyType.Name + "(" + propAccess + ")" );
            }else if(IsApiCollection(member.PropertyType)){

                string listType = member.PropertyType.GetGenericArguments()[0].Name;
                string collType = listType + "Collection";
                writer.WriteLine("self." + memberName + " = " + collType + "(" + propAccess + ")");
                
            }else{
                writer.WriteLine("#" + member.PropertyType.ToString());
            }
        }
        writer.ident --;

        writer.WriteLine();
        writer.WriteLine("def to_dict(self):");
        writer.ident ++;
        writer.WriteLine("json = {}" );

        foreach (var member in t.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            string memberName = CamelCase(member.Name);

            string propAccess = "json[" + Q(memberName) + "]";
            
            if(member.PropertyType.IsEnum){
                writer.WriteLine(propAccess + " = " + "self." + memberName + ".value");
            }else if(IsPrimitive(member.PropertyType)){
                writer.WriteLine(propAccess + " = " + "self." + memberName  );
            }else if(IsNullable(member.PropertyType) || IsSimpleCollection(member.PropertyType) || IsDictionary(member.PropertyType)){
                writer.WriteLine(propAccess + " = " + "self." + memberName  );
            }else if(IsApiType(member.PropertyType)){
                writer.WriteLine(propAccess + " = " + "self." + memberName + ".to_dict() if self." + memberName + " is not None else None");
            }else if(IsApiCollection(member.PropertyType)){
                writer.WriteLine(propAccess + " = " + "self." + memberName + ".to_dict() if self." + memberName + " is not None else None");                
            }else{
                writer.WriteLine("#" + member.PropertyType.ToString());
            }
        }
        writer.WriteLine("return json");
        writer.ident --;


        PrintConvertMethods(writer);

        writer.ident = 0;
        writer.WriteLine();

        writer.WriteLine("class " + t.Name + "Collection:");
        writer.ident ++;
        writer.WriteLine("def __init__(self, json):");
        writer.ident ++;
        writer.WriteLine("self.values = ["+ t.Name + "(p) for p in json]");
        writer.ident --;

        writer.WriteLine();

        writer.WriteLine("def to_dict(self):");
        writer.ident ++;
        writer.WriteLine("return [p.to_dict() for p in self.values]");
        writer.ident --;

        writer.WriteLine();

        writer.WriteLine("def __iter__(self):");
        writer.ident ++;
        writer.WriteLine("return iter(self.values)");
        writer.ident --;
        
        writer.WriteLine();
        writer.WriteLine("def __getitem__(self, item):");
        writer.ident ++;
        writer.WriteLine("return self.values[item]");
        writer.ident --;

        writer.WriteLine();
        writer.WriteLine("def __len__(self):");
        writer.ident ++;
        writer.WriteLine("return len(self.values)");
        writer.ident --;

        PrintConvertMethods(writer);
        writer.ident = 0;
        writer.WriteLine();
    }
}



public class IdentWriter{
    private StreamWriter writer;
    public int ident = 0;
    public IdentWriter(StreamWriter writer){
        this.writer = writer;
    }

    public void WriteLine(string text){
        string outText = "";
        for(int i = 0; i < this.ident; i++) outText += "    ";
        this.writer.WriteLine(outText + text);
    }
    public void WriteLine(){
        writer.WriteLine();
    }
}