/* tslint:disable */
/* eslint-disable */
/**
 * FastAPI
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { mapValues } from '../runtime';
/**
 * 
 * @export
 * @interface UISettingsCreate
 */
export interface UISettingsCreate {
    /**
     * 
     * @type {boolean}
     * @memberof UISettingsCreate
     */
    distanceText: boolean;
    /**
     * 
     * @type {boolean}
     * @memberof UISettingsCreate
     */
    distanceLine: boolean;
    /**
     * 
     * @type {boolean}
     * @memberof UISettingsCreate
     */
    landmarks: boolean;
    /**
     * 
     * @type {boolean}
     * @memberof UISettingsCreate
     */
    fixtures: boolean;
}

/**
 * Check if a given object implements the UISettingsCreate interface.
 */
export function instanceOfUISettingsCreate(value: object): value is UISettingsCreate {
    if (!('distanceText' in value) || value['distanceText'] === undefined) return false;
    if (!('distanceLine' in value) || value['distanceLine'] === undefined) return false;
    if (!('landmarks' in value) || value['landmarks'] === undefined) return false;
    if (!('fixtures' in value) || value['fixtures'] === undefined) return false;
    return true;
}

export function UISettingsCreateFromJSON(json: any): UISettingsCreate {
    return UISettingsCreateFromJSONTyped(json, false);
}

export function UISettingsCreateFromJSONTyped(json: any, ignoreDiscriminator: boolean): UISettingsCreate {
    if (json == null) {
        return json;
    }
    return {
        
        'distanceText': json['distance_text'],
        'distanceLine': json['distance_line'],
        'landmarks': json['landmarks'],
        'fixtures': json['fixtures'],
    };
}

export function UISettingsCreateToJSON(json: any): UISettingsCreate {
    return UISettingsCreateToJSONTyped(json, false);
}

export function UISettingsCreateToJSONTyped(value?: UISettingsCreate | null, ignoreDiscriminator: boolean = false): any {
    if (value == null) {
        return value;
    }

    return {
        
        'distance_text': value['distanceText'],
        'distance_line': value['distanceLine'],
        'landmarks': value['landmarks'],
        'fixtures': value['fixtures'],
    };
}
